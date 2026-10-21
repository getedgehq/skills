#!/usr/bin/env python3
"""Regression checks for non-Yes export values, invisible appearances and flattening."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

import fitz
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, NameObject
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import form_fill as ff


class VisibleCheckboxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        doc = fitz.open()
        page = doc.new_page(width=200,height=200)
        page.insert_text((25,35),'Sample LLC')
        for i, name in enumerate(['llc', 'other']):
            widget = fitz.Widget()
            widget.field_name = name
            widget.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
            widget.rect = fitz.Rect(25,50+i*25,33,58+i*25)
            page.add_widget(widget)
        original = self.root/'original.pdf'
        doc.save(original)
        doc.close()
        writer = PdfWriter(clone_from=original)
        for ident, pi, obj in ff.widgets(writer):
            normal = obj['/AP']['/N']
            on = next(k for k in normal if k != '/Off')
            ref = normal.raw_get(on)
            del normal[on]
            normal[NameObject('/6')] = ref
        self.source = self.root/'source.pdf'
        with self.source.open('wb') as out: writer.write(out)
        self.spec = {'fields':{'llc':'6','other':False}}

    def tearDown(self): self.tmp.cleanup()

    def test_non_yes_export_and_flatten(self):
        inv = ff.inventory(self.source)
        self.assertEqual(inv['widgets'][0]['on_values'], ['6'])
        for flatten in [False,True]:
            pdf = self.root/f'{flatten}.pdf'
            report = ff.fill(self.source,pdf,self.spec,self.root/f'e{flatten}',flatten)
            self.assertTrue(report['passed'])
            self.assertEqual(report['intended_ticks'],1)
            self.assertEqual(report['flattened'],flatten)
            self.assertTrue(report['checks'][0]['visible_tick'])

    def test_invisible_on_appearance_retries(self):
        writer = PdfWriter(clone_from=self.source)
        for ident, pi, obj in ff.widgets(writer):
            obj['/AP']['/N'][NameObject('/6')] = ff.appearance(writer,8,8)
        broken = self.root/'broken.pdf'
        with broken.open('wb') as out: writer.write(out)
        out = self.root/'repaired.pdf'
        report = ff.fill(broken,out,self.spec,self.root/'retry')
        self.assertEqual([a['passed'] for a in report['attempts']], [False,True])
        self.assertTrue(report['checks'][0]['visible_tick'])

    def test_metadata_only_tick_fails(self):
        inv = ff.inventory(self.source)
        vals = ff.resolve(inv,self.spec)
        fake = self.root/'metadata-only.pdf'
        ff.build(self.source,fake,inv,vals,all_off=True)
        writer = PdfWriter(clone_from=fake)
        obj = next(ff.widgets(writer))[2]
        # Claim a selected field, but retain the Off appearance.
        obj[NameObject('/V')] = NameObject('/6')
        with fake.open('wb') as out: writer.write(out)
        report = ff.verify(self.source,fake,self.spec,self.root/'negative')
        self.assertFalse(report['passed'])
        self.assertFalse(report['checks'][0]['visible_tick'])
        self.assertFalse(report['metadata_checks'][0]['passed'])

    def test_unintended_tick_fails(self):
        inv = ff.inventory(self.source)
        both = {'fields':{'llc':'6','other':'6'}}
        candidate = self.root/'both.pdf'
        ff.build(self.source,candidate,inv,ff.resolve(inv,both),regenerate=True)
        report = ff.verify(self.source,candidate,self.spec,self.root/'wrong-choice')
        self.assertFalse(report['passed'])
        self.assertFalse(report['checks'][1]['passed'])

    def test_unknown_and_wrong_export_rejected(self):
        inv = ff.inventory(self.source)
        for fields in [{'missing':'x'},{'llc':'Yes'},{'llc':'true'}]:
            with self.assertRaises(ValueError): ff.resolve(inv,{'fields':fields})


if __name__ == '__main__': unittest.main(verbosity=2)
