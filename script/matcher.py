#!/usr/bin/env python
evernote_file = open('evernote_in', 'r')
highlight_file = open('highlight_in','r')

class Log:
    info = 1
    debug = 2

log_level = Log.info
log = ''

def log_append(string, level=Log.info):
    global log
    if level <= log_level:
        log += string + '\n'

def log_flush():
    global log
    if len(log) > 0:
        print log
        log = ''

def log_delete():
    global log
    log = ''

def matching_indexes(string, text):
    if len(string) > len(text): return None

    matching_idxs = []
    start_idx = text.find(string[0], 0) #start with the first match of the first character of the highlight
    while start_idx != -1: #if the first character match, go ahead matching all the subsequent chars of string
        log_append('highlight: "' + string + '"', Log.debug)
        log_append('moving to next occurrence at index: (%d, %d)' % (start_idx, start_idx + len(string)), Log.debug)
        log_append('---\n(%d,%d): %s \n---' % (start_idx, start_idx + len(string), text[start_idx:start_idx + len(string)]), Log.debug)
        end_idx = None 
        tag_offset = 0
        str_idx = 0
        while str_idx < len(string): 
            text_idx = start_idx + str_idx + tag_offset
            if string[str_idx] == text[text_idx]:
                end_idx = text_idx
                log_append(string[str_idx] + '(' + str(str_idx) + ')' + '==' + text[text_idx] + '(' + str(text_idx) + ')', Log.debug)
                str_idx += 1
            else:
                if text[text_idx] == '<': #if we find a '<' character (not present in the highlight string, we search for the tag close character and, using the tag offset variable, we "jump" till the end of the tag to continue the matching attempt
                    log_append('starting tag at ' + str(text_idx), Log.debug)
                    tag_end_idx = text.find('>', text_idx)
                    if tag_end_idx != -1:
                        log_append('found tag at ' + str(text_idx) + '-' + str(tag_end_idx), Log.debug)
                        tag_offset += tag_end_idx - text_idx + 1
                else:
                    end_idx = None
                    log_delete()
                    log_append('BUM - ' + string[str_idx] + '(' + str(str_idx) + ')' + '!=' + text[text_idx] + '(' + str(text_idx) + ')', Log.debug)
                    break     #when you encounter a character not matching the matching series is broken, thus go ahead breaking the loop
        if end_idx != None:     #if at the end of the matching series the end index is valid it means we have a match! add it to the matching_idxs list
            matching_idxs.append((start_idx, end_idx))
            log_flush()
        start_idx = text.find(string[0], start_idx + 1) #compute the next matching index of the first character to begin a new matching series attempt
    return matching_idxs 

def match_highlight(highlight, text):
    #TODO: improve using UNICODE
    return matching_indexes(highlight, text) 

def main():    
    original_note = evernote_file.read()
    for highlight in highlight_file:
        #remove the pipe delimiter and strip leading/trailing whitespaces
       highlight = highlight.replace('|','').strip()
       print '"' + highlight + '"' + "\nmatches at: " + str(match_highlight(highlight, original_note))

if __name__ == '__main__':
    main()

