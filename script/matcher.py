#!/usr/bin/env python
evernote_file = open('evernote_in', 'r')
highlight_file = open('highlight_in','r')

def matching_indexes(string, text):
    if len(string) > len(text): return None

    matching_idxs = []
    start_idx = text.find(string[0], 0) #start with the first match of the first character of the highlight
    while start_idx != -1: #if the first character match, go ahead matching all the subsequent chars of string
        end_idx = None 
        for i in range(len(string)):
            #print  string[i] + ' testing with ' + text[start_idx+i],
            if string[i] != text[start_idx+i]:
                end_idx = None
                #print ' does not match'
                #print ' --------------\n\n'
                break     #when you encounter a character not matching the matching series is broken, thus go ahead breaking the loop
            else:
                end_idx = start_idx + i
                #print ' matches at ' + str(end_idx)
        if end_idx != None:     #if at the end of the matching series the end index is valid it means we have a match! add it to the matching_idxs list
            #print '-> match found at (%d, %d)' % (start_idx, end_idx)
            matching_idxs.append((start_idx, end_idx))
        start_idx = text.find(string[0], start_idx + len(string)) #compute the next matching index of the first character to begin a new matching series attempt
    return matching_idxs 

def match_highlight(highlight, text):
    #TODO: improve using UNICODE
    return matching_indexes(highlight, text) 

def main():    
    original_note = evernote_file.read()
    for highlight in highlight_file:
        #remove the pipe delimiter and strip leading/trailing whitespaces
       highlight = highlight.replace('|','').strip()
       print highlight + " matches at: " + str(match_highlight(highlight, original_note))

if __name__ == '__main__':
    main()

