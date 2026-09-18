"""Reject unsafe script provenance and preserve timeline context in displays."""
import unittest
from scripts import validate_source_yaml as validator
from scripts.generate_book_seed import format_source_line, render

class ScriptSourceTests(unittest.TestCase):
    def test_script_paths_use_existing_chapter_carrier(self):
        self.assertIsNotNone(validator.BOOK_SOURCE_NAME_RE.match('book-cc/chapter-29-p1-a2-s10.yaml'))

    def test_script_source_line_keeps_scene_page_and_id_with_url(self):
        entry = {'source_id':'CC','scene_id':'CC-P1-A2-S10','source_url':'https://example.org/a.pdf',
                 'pdf_page':99,'id':'cc-p1-a2-s10-001','_output_yaml':'sources/book-cc/chapter-29-p1-a2-s10.yaml'}
        line = format_source_line(entry)
        for value in ['CC-P1-A2-S10', '99', 'cc-p1-a2-s10-001']:
            self.assertIn(value,line)

    def test_generated_seed_keeps_altered_timeline_context(self):
        entry = {'id':'cc-p1-a2-s10-001','source_note':'Portraits advise the head.',
                 'timeline':'altered','timeline_detail':'First altered branch',
                 'evidence_mode':'dialogue_claim','speaker':'McGonagall',
                 'era_classification':'later_editorial_note'}
        output = render([entry])
        self.assertIn('First altered branch',output)
        self.assertIn('dialogue_claim',output)

class TimelineValidationTests(unittest.TestCase):
    def entry(self):
        return {'id':'cc-p1-a2-s10-001','source_id':'CC','scene_id':'CC-P1-A2-S10',
                'part':1,'act':2,'scene':10,'pdf_page':99,'timeline':'altered',
                'timeline_detail':'First altered world','evidence_mode':'dialogue_claim',
                'speaker':'McGonagall','historical_period':'2020',
                'information_available':'Heard in altered 2020','character_knowledge':'Explained to Harry',
                'bagshot_1984_access':'Not established','era_classification':'later_editorial_note',
                'comparison':{'relation':'new_information','related_ids':[]}}

    def scene(self):
        return {'scene_id':'CC-P1-A2-S10','part':1,'act':2,'scene':10,'page_start':99,'page_end':100}

    def test_altered_history_cannot_be_original_book_evidence(self):
        entry = self.entry()
        entry['era_classification'] = 'original_book_core_candidate'
        errors = validator.validate_script_entry(entry, self.scene(), set())
        self.assertTrue(any('altered' in e for e in errors))

    def test_scene_locator_and_related_ids_are_checked(self):
        entry = self.entry()
        entry['pdf_page'] = 121
        entry['comparison']['related_ids'] = ['nonexistent']
        errors = validator.validate_script_entry(entry,self.scene(),set())
        self.assertTrue(any('page' in e for e in errors))
        self.assertTrue(any('nonexistent' in e for e in errors))

    def test_qualified_altered_record_is_valid(self):
        self.assertEqual(validator.validate_script_entry(self.entry(),self.scene(),set()),[])

class ScriptProvenanceRegressionTests(unittest.TestCase):
    entry = TimelineValidationTests.entry
    scene = TimelineValidationTests.scene
    def test_bad_comparison_reports_error(self):
        entry = self.entry()
        entry['comparison'] = 'bad type'
        errors = validator.validate_script_entry(entry,self.scene(),set())
        self.assertTrue(any('comparison' in e for e in errors))

    def test_wrong_portable_carrier_and_bounds_are_rejected(self):
        entry = self.entry()
        entry.update(source_file='pdfs/WRONG.pdf',chapter_start_pdf_page=500,chapter_end_pdf_page=600)
        scene = self.scene()
        scene['source_file'] = 'pdfs/harry-potter-and-the-cursed-child.pdf'
        errors = validator.validate_script_entry(entry,scene,set())
        self.assertTrue(any('source_file' in e for e in errors))
        self.assertTrue(any('chapter_start' in e for e in errors))

class ScriptPassageTests(unittest.TestCase):
    def test_changed_or_out_of_range_passage_is_rejected(self):
        import hashlib
        text = 'HARRY: A brief statement.'
        entry = {'id':'cc-example','passage_locator':{'char_start':7,'char_end':12,
                 'text_sha256':hashlib.sha256(text[7:12].encode()).hexdigest()}}
        self.assertEqual(validator.validate_script_passage(entry,text),[])
        self.assertTrue(validator.validate_script_passage(entry,text.replace('brief','wrong')))
        entry['passage_locator']['char_end'] = 200
        self.assertTrue(validator.validate_script_passage(entry,text))

class ScriptAppendixTests(unittest.TestCase):
    def test_script_is_not_mislabeled_external_and_retains_timeline(self):
        from scripts.generate_appendices import external_source_label, entry_label
        row = {'source_id':'CC','scene_id':'CC-P1-A2-S10','pdf_page':100,
               'id':'cc-p1-a2-s10-002','_book':'Cursed Child','_chapter':'Act 2 Scene 10',
               'timeline':'altered','timeline_detail':'First altered world','source_note':'Portrait claim.'}
        self.assertIsNone(external_source_label(row))
        label = entry_label(row)
        self.assertIn('CC-P1-A2-S10',label)
        self.assertIn('100',label)
        self.assertIn('First altered world',label)
