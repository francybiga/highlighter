#!/usr/bin/env python

import yaml
import os
import logging

from subprocess import call

from matcher import match_highlight_file_to_note

from evernote.api.client import EvernoteClient
from evernote.api.client import NoteStore
from evernote.edam.type.ttypes import Note

def copyNoteWithNewContent(original_note, content, notebook_guid):
        hl_note = Note()
        hl_note.title = original_note.title
        hl_note.content = content
        hl_note.resources = original_note.resources
        hl_note.notebookGuid = notebook_guid
        hl_note.tagGuids = original_note.tagGuids
        hl_note.attributes = original_note.attributes
        return hl_note

def main():

    logging.basicConfig(format='%(message)s', level=logging.INFO)

    #Load configuration
    config = yaml.load(open('config.yml', 'r'))
    highlights_dir = config['highlights_dir']
    highlights_backup_dir = highlights_dir + 'backup/'
    input_notebook_name = config['input_notebook_name']
    output_notebook_name = config['output_notebook_name']
    backup_notebook_name = config['backup_notebook_name']
    dev_token = config['dev_token']

    logging.info('----------------------------')
    logging.info('Configuration:')
    logging.info('----------------------------')
    logging.info('highlights_dir: %s', highlights_dir)
    logging.info('highlights_backup_dir: %s', highlights_backup_dir)
    logging.info('input_notebook_name: %s', input_notebook_name)
    logging.info('output_notebook_name: %s', output_notebook_name)
    logging.info('backup_notebook_name: %s', backup_notebook_name)
    logging.info('dev_token %s', dev_token)
    logging.info('----------------------------\n')

    #Initialize Evernote stack
    client = EvernoteClient(token=dev_token, sandbox=False)
    note_store = client.get_note_store()
    notebooks = note_store.listNotebooks()

    #Get the notebooks GUIDs
    out_notebook_guid = None
    in_notebook_guid = None
    backup_notebook_guid = None
    for notebook in notebooks:
        if notebook.name == input_notebook_name:
            in_notebook_guid = notebook.guid 
        if notebook.name == output_notebook_name:
            out_notebook_guid = notebook.guid
        if notebook.name == backup_notebook_name:
            backup_notebook_guid = notebook.guid
                
    #Get the notes to be highlghted
    search_filter = NoteStore.NoteFilter()
    search_filter.notebookGuid = in_notebook_guid 

    notes_metadata_spec = NoteStore.NotesMetadataResultSpec()
    notes_metadata_spec.includeTitle = True

    notes_meta_list = note_store.findNotesMetadata(dev_token, search_filter, 0, 100, notes_metadata_spec).notes

    hl_files = [name for name in os.listdir(highlights_dir) if name.endswith('.txt')]
    if len(hl_files) == 0:
        logging.info('zero highlight text file found')
        return

    matched_notes = 0
    new_notes_titles = []
    for hl_filename in hl_files:
        hl_filename_no_ext = os.path.splitext(hl_filename)[0]
        for note_meta in notes_meta_list:
            note_transformed_title = note_meta.title.replace(' ', '_').lower()
            if note_transformed_title == hl_filename_no_ext: 
                matched_notes += 1
                logging.info('Matching note found:')
                logging.info('title: %s', note_meta.title)
                logging.info('hl text file: %s\n', hl_filename_no_ext)
                number_of_hl = call(['wc -l %s', hl_filename])
                logging.info('nuber of highlights: %d', number_of_hl)

                original_note = note_store.getNote(dev_token, note_meta.guid, True, False, False, False)

                #match highlight in note content
                os.chdir(highlights_dir)
                hl_file_path = os.path.abspath(hl_filename)
                hl_content = match_highlight_file_to_note(hl_file_path, original_note.content)
                
                #create new note with the highlighted content and save it to the output notebook
                hl_note = copyNoteWithNewContent(original_note, hl_content, out_notebook_guid)
                note_store.createNote(dev_token, hl_note)
                logging.info('created new higlighted note: %s', hl_note.title)
                new_notes_titles.append(hl_note.title) 

                #move old note to the backup notebook (if present)
                if backup_notebook_guid:
                    original_note.notebookGuid = backup_notebook_guid
                    note_store.updateNote(dev_token, original_note)
                    logging.info('moved original note to the backup notebook')

                #move the highlight text file to a proper subfolder 
                if not os.path.isdir(highlights_backup_dir):
                    logging.info('creating backup dir at: %s', highlights_backup_dir)
                    os.mkdir(highlights_backup_dir)
                hl_backup_file_path = highlights_backup_dir + hl_filename
                os.rename(hl_file_path, hl_backup_file_path)
                logging.info('moved highlight text file to backup folder')
    logging.info('----------------------------')
    logging.info('Done! %d notes matched', matched_notes)
    for title in new_notes_titles:
        logging.info('\t* %s', title)
    logging.info('----------------------------')

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()

