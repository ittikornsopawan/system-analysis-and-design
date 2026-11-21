"""Project-independent draw.io geometry, native cells and editable PNG validation.

No renderer or palette is imposed. Run verify_diagram.py for the artifact CLI.
"""
from __future__ import annotations
import base64
import math
from pathlib import Path
import struct
from urllib.parse import unquote
import xml.etree.ElementTree as ET
import zlib

def rounded_path(points, radius=8, min_radius=6):
    if len(points) < 2:
        raise ValueError("A route needs two or more points")
    commands=[f'M {points[0][0]:g} {points[0][1]:g}']
    for a,b,c in zip(points,points[1:],points[2:]):
        da,dc=math.dist(a,b),math.dist(b,c)
        r=min(radius,da/2,dc/2)
        if not da or not dc or r < min_radius:
            raise ValueError("Route has a degenerate or undersized corner")
        p=(b[0]+(a[0]-b[0])*r/da,b[1]+(a[1]-b[1])*r/da)
        q=(b[0]+(c[0]-b[0])*r/dc,b[1]+(c[1]-b[1])*r/dc)
        commands.append(f'L {p[0]:g} {p[1]:g} Q {b[0]:g} {b[1]:g} {q[0]:g} {q[1]:g}')
    commands.append(f'L {points[-1][0]:g} {points[-1][1]:g}')
    return ' '.join(commands)


def overlap(a,b):
    return a[0]<b[0]+b[2] and b[0]<a[0]+a[2] and a[1]<b[1]+b[3] and b[1]<a[1]+a[3]


def segment_hits_box(p,q,box):
    x,y,w,h=box
    if p[1]==q[1]:return y<p[1]<y+h and max(min(p[0],q[0]),x)<min(max(p[0],q[0]),x+w)
    return x<p[0]<x+w and max(min(p[1],q[1]),y)<min(max(p[1],q[1]),y+h)


def xml_signature(e):
    return e.tag,tuple(sorted(e.attrib.items())),(e.text or '').strip(),tuple(xml_signature(c) for c in e)


def add_cell(root,key,value,x,y,w,h,style,parent='1',edge=False,points=None):
    c=ET.SubElement(root,'mxCell',id=key,value=value,style=style,parent=parent,**({'edge':'1'} if edge else {'vertex':'1'}))
    geo=ET.SubElement(c,'mxGeometry',attrib={'as':'geometry'})
    if edge:
        geo.set('relative','1');p=points
        ET.SubElement(geo,'mxPoint',x=f'{p[0][0]:g}',y=f'{p[0][1]:g}',attrib={'as':'sourcePoint'})
        ET.SubElement(geo,'mxPoint',x=f'{p[-1][0]:g}',y=f'{p[-1][1]:g}',attrib={'as':'targetPoint'})
        if len(p)>2:
            a=ET.SubElement(geo,'Array',attrib={'as':'points'})
            for px,py in p[1:-1]:ET.SubElement(a,'mxPoint',x=f'{px:g}',y=f'{py:g}')
    else:
        for k,v in dict(x=x,y=y,width=w,height=h).items():geo.set(k,f'{v:g}')
    return c


PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'
MAX_XML_BYTES = 64 * 1024 * 1024


def inflate(data, wbits=zlib.MAX_WBITS):
    decoder = zlib.decompressobj(wbits)
    result = decoder.decompress(data, MAX_XML_BYTES + 1)
    if len(result) > MAX_XML_BYTES or decoder.unconsumed_tail:
        raise ValueError('Editable model exceeds decompression limit')
    if not decoder.eof or decoder.unused_data:
        raise ValueError('Incomplete or trailing compressed model')
    return result


def parse_xml(data):
    if len(data) > MAX_XML_BYTES:
        raise ValueError('Editable model exceeds XML limit')
    text = data.decode('utf-8') if isinstance(data, bytes) else data
    if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper():
        raise ValueError('DTD/entity declarations are unsupported')
    return ET.fromstring(text)


def models(data):
    """Read raw mxGraphModel, uncompressed mxfile or native compressed pages."""
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    root = parse_xml(data.lstrip('\ufeff')) if data.lstrip('\ufeff \t\r\n').startswith('<') else parse_xml(unquote(data))
    if root.tag == 'mxGraphModel':
        return [root]
    if root.tag != 'mxfile':
        raise ValueError('Expected mxfile or mxGraphModel')
    result = []
    for page in root.findall('diagram'):
        graph = page.find('mxGraphModel')
        if graph is None:
            raw = base64.b64decode((page.text or '').strip(), validate=True)
            graph = parse_xml(unquote(inflate(raw, -15).decode('utf-8')))
        if graph.tag != 'mxGraphModel':
            raise ValueError('Invalid diagram page')
        result.append(graph)
    if not result:
        raise ValueError('No editable pages')
    return result


def png_chunks(raw):
    if not raw.startswith(PNG_SIGNATURE):
        raise ValueError('Not a PNG')
    cursor, chunks = 8, []
    while cursor < len(raw):
        if cursor + 12 > len(raw):
            raise ValueError('Truncated PNG chunk')
        size = struct.unpack('>I', raw[cursor:cursor+4])[0]
        end = cursor + size + 12
        if end > len(raw):
            raise ValueError('Truncated PNG payload')
        kind, payload = raw[cursor+4:cursor+8], raw[cursor+8:end-4]
        crc = struct.unpack('>I', raw[end-4:end])[0]
        if zlib.crc32(kind+payload) & 0xffffffff != crc:
            raise ValueError('Invalid PNG CRC')
        chunks.append((kind, payload))
        cursor = end
        if kind == b'IEND':
            if payload or cursor != len(raw):
                raise ValueError('Invalid PNG end')
            break
    if not chunks or chunks[0][0] != b'IHDR' or len(chunks[0][1]) != 13:
        raise ValueError('Missing/invalid PNG header')
    if chunks[-1][0] != b'IEND' or not any(k == b'IDAT' for k, _ in chunks):
        raise ValueError('Incomplete PNG')
    if sum(k == b'IHDR' for k, _ in chunks) != 1:
        raise ValueError('Duplicate PNG header')
    width, height = struct.unpack('>II', chunks[0][1][:8])
    if not width or not height:
        raise ValueError('Invalid PNG dimensions')
    return chunks


def editable_payloads(chunks):
    result = []
    for kind, payload in chunks:
        if kind not in {b'tEXt', b'zTXt', b'iTXt'}:
            continue
        key, separator, body = payload.partition(b'\0')
        if key not in {b'mxfile', b'mxGraphModel'}:
            continue
        if not separator:
            raise ValueError('Malformed editable metadata')
        if kind == b'zTXt':
            if not body or body[0] != 0:
                raise ValueError('Unsupported PNG text compression')
            body = inflate(body[1:])
        elif kind == b'iTXt':
            if len(body) < 2 or body[0] not in (0, 1) or body[1] != 0:
                raise ValueError('Unsupported PNG international text compression')
            flag = body[0]
            # compression flag/method, language tag, translated keyword, text
            fields = body[2:].split(b'\0', 2)
            if len(fields) != 3:
                raise ValueError('Malformed PNG international text')
            body = inflate(fields[2]) if flag else fields[2]
        result.append((key, body))
    if not result:
        raise ValueError('Editable PNG model missing')
    return result


def validate_model(graph, require_nested=False):
    cells = graph.findall('./root/mxCell') + graph.findall('./root/*/mxCell')
    # Some draw.io cells are wrapped in <object id=...>.
    ids = {}
    for cell in cells:
        key = cell.get('id')
        if key is None:
            wrapper = next((e for e in graph.findall('./root/*') if cell in list(e)), None)
            key = wrapper.get('id') if wrapper is not None else None
        if not key or key in ids:
            raise ValueError('Missing or duplicate cell id')
        ids[key] = cell
    if not cells or '0' not in ids:
        raise ValueError('Missing root cell')
    nested = False
    for key, cell in ids.items():
        for attr in ('parent', 'source', 'target'):
            ref = cell.get(attr)
            if ref is not None and ref not in ids:
                raise ValueError(f'Missing {attr}: {ref}')
        seen, current = {key}, cell.get('parent')
        while current is not None:
            if current in seen:
                raise ValueError('Cell parent cycle')
            seen.add(current)
            current = ids[current].get('parent')
        parent = ids.get(cell.get('parent'))
        if cell.get('vertex') == '1' and parent is not None and parent.get('vertex') == '1':
            nested = True
    if require_nested and not nested:
        raise ValueError('No native child vertex inside a vertex container')
    return len(cells)


def verify_artifact(source_path, png_path, require_nested=False, roundtrip=None, max_bytes=None):
    graphs = models(Path(source_path).read_bytes())
    count = sum(validate_model(g, require_nested) for g in graphs)
    raw = Path(png_path).read_bytes()
    chunks = png_chunks(raw)
    expected = [xml_signature(g) for g in graphs]
    for _, payload in editable_payloads(chunks):
        if [xml_signature(g) for g in models(payload)] != expected:
            raise ValueError('Embedded model differs from source')
    if max_bytes is not None and len(raw) > max_bytes:
        raise ValueError(f'PNG size exceeds {max_bytes} bytes')
    if roundtrip is not None:
        other = png_chunks(Path(roundtrip).read_bytes())
        if chunks[0][1] != other[0][1] or b''.join(v for k,v in chunks if k == b'IDAT') != b''.join(v for k,v in other if k == b'IDAT'):
            raise ValueError('Same-renderer PNG header/pixel stream differs')
    return {'pages': len(graphs), 'cells': count, 'width': struct.unpack('>I',chunks[0][1][:4])[0],
            'height': struct.unpack('>I',chunks[0][1][4:8])[0], 'bytes': len(raw)}


def finalize_png(source_path, png_path):
    """Add mxfile compatibility metadata after native export; retain pixel bytes."""
    verify_artifact(source_path, png_path)
    chunks = png_chunks(Path(png_path).read_bytes())
    native = next((p for k,p in editable_payloads(chunks) if k == b'mxGraphModel'), None)
    if native is None:
        raise ValueError('Native mxGraphModel metadata required for finalization')
    result = bytearray(PNG_SIGNATURE)
    for kind, payload in chunks:
        if kind in {b'tEXt',b'zTXt',b'iTXt'} and payload.split(b'\0',1)[0] == b'mxfile':
            continue
        if kind == b'IEND':
            extra = b'mxfile\0\0' + zlib.compress(native,9)
            result += struct.pack('>I',len(extra))+b'zTXt'+extra+struct.pack('>I',zlib.crc32(b'zTXt'+extra)&0xffffffff)
        result += struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff)
    after = png_chunks(result)
    if b''.join(v for k,v in chunks if k == b'IDAT') != b''.join(v for k,v in after if k == b'IDAT'):
        raise ValueError('Finalization changed pixel bytes')
    Path(png_path).write_bytes(result)
    return struct.unpack('>II', after[0][1][:8])
