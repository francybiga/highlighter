#!/usr/bin/env python

import logging

def match_highlight(string, text):
    if len(string) > len(text): return None

    matching_idxs = []
    start_idx = text.find(string[0], 0) #start with the first match of the first character of the highlight
    while start_idx != -1: #if the first character match, go ahead matching all the subsequent chars of string
        logging.debug('highlight: "' + string + '"')
        logging.debug('moving to next occurrence at index: (%d, %d)' % (start_idx, start_idx + len(string)))
        logging.debug('---\n(%d,%d): %s \n---' % (start_idx, start_idx + len(string), text[start_idx:start_idx + len(string)]))
        end_idx = None 
        tag_offset = 0
        str_idx = 0
        while str_idx < len(string): 
            text_idx = start_idx + str_idx + tag_offset
            if string[str_idx] == text[text_idx]:
                end_idx = text_idx
                logging.debug(string[str_idx] + '(' + str(str_idx) + ')' + '==' + text[text_idx] + '(' + str(text_idx) + ')')
                str_idx += 1
            else:
                if text[text_idx] == '<': #if we find a '<' character (not present in the highlight string, we search for the tag close character and, using the tag offset variable, we "jump" till the end of the tag to continue the matching attempt
                    logging.debug('starting tag at ' + str(text_idx))
                    tag_end_idx = text.find('>', text_idx)
                    if tag_end_idx != -1:
                        logging.debug('found tag at ' + str(text_idx) + '-' + str(tag_end_idx))
                        tag_offset += tag_end_idx - text_idx + 1
                else:
                    end_idx = None
                    logging.debug('BUM - ' + string[str_idx] + '(' + str(str_idx) + ')' + '!=' + text[text_idx] + '(' + str(text_idx) + ')')
                    start_idx = text.find(string[0], start_idx + 1) #compute the next matching index of the first character to begin a new matching series attempt
                    break     #when you encounter a character not matching the matching series is broken, thus go ahead breaking the loop
        if end_idx != None:     
            hl_opening_tag = '<span style="background-color: rgb(255, 250, 165);-evernote-highlight:true">'
            hl_closing_tag = '</span>'
            logging.debug('old text: ' + text[start_idx:end_idx+1])
            text = text[:start_idx] + hl_opening_tag + text[start_idx:end_idx+1] + hl_closing_tag + text[end_idx+1:]
            end_idx = end_idx + len(hl_opening_tag) + len(hl_closing_tag)#we should recompute the end idx adding the size of the opening tag
            logging.debug('new text: ' + text[start_idx:end_idx + 1])
            logging.debug('starting new search from index ' + str(end_idx))
            start_idx = text.find(string[0], end_idx)
    return text 

def match_highlight_file_to_note(highlight_path, note_content):
    highlight_file = open(highlight_path, 'r')

    for highlight in highlight_file: 
        #remove the pipe delimiter and strip leading/trailing whitespaces
        highlight = highlight.replace('|','').strip()
        note_content = match_highlight(highlight, note_content)

    highlight_file.close()
    return note_content

