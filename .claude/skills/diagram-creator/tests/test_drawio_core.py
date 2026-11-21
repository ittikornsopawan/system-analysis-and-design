"""Artifact-level regressions: damaged PNGs, stale models and false hierarchy."""
import base64
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from urllib.parse import quote
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from drawio_core import (PNG_SIGNATURE, finalize_png, models, png_chunks,
                         verify_artifact, xml_signature)

GRAPH = '''<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>
<mxCell id="layer" parent="1" vertex="1"><mxGeometry x="0" y="0" width="100" height="100" as="geometry"/></mxCell>
<mxCell id="child" parent="layer" vertex="1"><mxGeometry x="10" y="20" width="40" height="20" as="geometry"/></mxCell>
</root></mxGraphModel>'''
SOURCE = '<mxfile><diagram id="page">' + GRAPH + '</diagram></mxfile>'


def chunk(kind, data):
    return struct.pack('>I',len(data)) + kind + data + struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)


def png(source=SOURCE, metadata='zTXt', pixel=b'\xff\x00\x00'):
    payload = quote(source, safe='').encode()
    if metadata == 'zTXt':
        text = chunk(b'zTXt', b'mxGraphModel\0\0'+zlib.compress(payload))
    elif metadata == 'iTXt':
        text = chunk(b'iTXt', b'mxfile\0\1\0\0\0'+zlib.compress(payload))
    elif metadata == 'tEXt':
        text = chunk(b'tEXt', b'mxfile\0'+payload)
    else:
        text = b''
    return PNG_SIGNATURE + chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,2,0,0,0)) + text + chunk(b'IDAT', zlib.compress(b'\0'+pixel)) + chunk(b'IEND',b'')


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name)/'view.drawio'
        self.image = Path(self.tmp.name)/'view.drawio.png'
        self.source.write_text(SOURCE)
        self.image.write_bytes(png())

    def test_valid_native_and_text_encodings(self):
        for encoding in ('zTXt','iTXt','tEXt'):
            with self.subTest(encoding=encoding):
                self.image.write_bytes(png(metadata=encoding))
                result = verify_artifact(self.source,self.image,require_nested=True)
                self.assertEqual((result['pages'],result['cells'],result['width']), (1,4,1))

    def test_compressed_drawio_page(self):
        encoder = zlib.compressobj(wbits=-15)
        encoded = base64.b64encode(encoder.compress(quote(GRAPH).encode())+encoder.flush()).decode()
        source = '<mxfile><diagram>'+encoded+'</diagram></mxfile>'
        self.source.write_text(source)
        self.assertEqual(xml_signature(models(source)[0]),xml_signature(models(SOURCE)[0]))
        verify_artifact(self.source,self.image,True)

    def test_finalize_preserves_pixels_and_is_idempotent(self):
        before = [p for k,p in png_chunks(self.image.read_bytes()) if k == b'IDAT']
        self.assertEqual(finalize_png(self.source,self.image),(1,1))
        first = self.image.read_bytes()
        finalize_png(self.source,self.image)
        self.assertEqual(first,self.image.read_bytes())
        self.assertEqual(before,[p for k,p in png_chunks(first) if k == b'IDAT'])
        verify_artifact(self.source,self.image,True)

    def test_missing_metadata(self):
        self.image.write_bytes(png(metadata=None))
        with self.assertRaisesRegex(ValueError,'model missing'):
            verify_artifact(self.source,self.image)

    def test_corrupt_crc_and_truncated_png(self):
        corrupt = bytearray(png());corrupt[-1] ^= 1
        for data in (corrupt,png()[:-3],png()+b'extra'):
            with self.subTest(size=len(data)), self.assertRaises(ValueError):
                png_chunks(data)

    def test_stale_embedded_source(self):
        self.image.write_bytes(png(SOURCE.replace('id="child"','id="other"')))
        before = self.image.read_bytes()
        with self.assertRaisesRegex(ValueError,'differs'):
            finalize_png(self.source,self.image)
        self.assertEqual(before,self.image.read_bytes())

    def test_missing_parent_duplicate_id_cycle_and_endpoint(self):
        variants = [SOURCE.replace('parent="layer"','parent="missing"'),
                    SOURCE.replace('id="child"','id="layer"'),
                    SOURCE.replace('id="layer" parent="1"','id="layer" parent="child"'),
                    SOURCE.replace('id="child" parent="layer"','id="child" source="missing" parent="layer"')]
        for source in variants:
            with self.subTest(source=source):
                self.source.write_text(source);self.image.write_bytes(png(source))
                with self.assertRaises(ValueError):
                    verify_artifact(self.source,self.image)

    def test_background_box_is_not_native_containment(self):
        flat = SOURCE.replace('parent="layer"','parent="1"')
        self.source.write_text(flat);self.image.write_bytes(png(flat))
        verify_artifact(self.source,self.image)
        with self.assertRaisesRegex(ValueError,'No native child'):
            verify_artifact(self.source,self.image,True)

    def test_all_embedded_entries_must_match(self):
        raw = png()
        extra = chunk(b'tEXt',b'mxfile\0'+quote(SOURCE.replace('id="child"','id="other"')).encode())
        self.image.write_bytes(raw[:-12]+extra+raw[-12:])
        with self.assertRaisesRegex(ValueError,'differs'):
            verify_artifact(self.source,self.image)

    def test_size_and_same_renderer_pixel_stream(self):
        other = Path(self.tmp.name)/'roundtrip.png';other.write_bytes(png())
        verify_artifact(self.source,self.image,roundtrip=other)
        with self.assertRaisesRegex(ValueError,'size exceeds'):
            verify_artifact(self.source,self.image,max_bytes=1)
        other.write_bytes(png(pixel=b'\0\0\0'))
        with self.assertRaisesRegex(ValueError,'pixel stream differs'):
            verify_artifact(self.source,self.image,roundtrip=other)

    def test_reject_entity_declarations(self):
        with self.assertRaisesRegex(ValueError,'DTD/entity'):
            models('<!DOCTYPE mxfile [<!ENTITY x "bad">]>'+SOURCE)


if __name__ == '__main__':
    unittest.main()
