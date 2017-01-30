#!/usr/bin/env python

import yaml
import os

from matcher import match_highlight_file_to_note

from evernote.api.client import EvernoteClient
from evernote.api.client import NoteStore

#Load configuration
config = yaml.load(open('config.yml', 'r'))
highlights_dir = config['highlights_dir']
input_notebook_name = config['input_notebook_name']
output_notebook_name = config['output_notebook_name']
dev_token = config['dev_token']

#Initialize Evernote stack
client = EvernoteClient(token=dev_token)
note_store = client.get_note_store()
notebooks = note_store.listNotebooks()

#Get the input notebook GUID
hl_notebook_guid = None
for notebook in notebooks:
    if notebook.name == input_notebook_name:
        hl_notebook_guid = notebook.guid
            
#Get the notes to be highlghted
search_filter = NoteStore.NoteFilter()
search_filter.notebookGuid = hl_notebook_guid

notes_metadata_spec = NoteStore.NotesMetadataResultSpec()
notes_metadata_spec.includeTitle = True

notes_meta_list = note_store.findNotesMetadata(dev_token, search_filter, 0, 100, notes_metadata_spec).notes

for hl_filename in [name for name in os.listdir(highlights_dir) if name.endswith('.txt')]:
    hl_filename_no_ext = os.path.splitext(hl_filename)[0]
for note_meta in notes_meta_list:
    note_transformed_title = note_meta.title.replace(' ', '_').lower()
    if note_transformed_title == hl_filename_no_ext: 
        #print 'Found matching notename: '
        #print hl_filename
        #print note_meta.guid + ' : ' + note_meta.title

        note = note_store.getNote(dev_token, note_meta.guid, True, False, False, False)

        #match highlight in note content
        #hl_file_path = highlights_dir + hl_filename 
        os.chdir(highlights_dir)
        hl_file_path = os.path.abspath(hl_filename)
        highlighted_content = match_highlight_file_to_note(hl_file_path, note.content)
        


