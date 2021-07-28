import os

class Parser():
    def __init__(self):
        self.longest_page = ""      # page with most words in it
        self.most_words = 0         # most words in a page
        self.common_words = dict()  # common words 
        self.unique_pages = set()   # unique pages among every domain/subdomain
        self.subdomains = dict()    # subdomain as key, num of pages as value
        self.domains = set()        # includes domains and subdomains
        self.word_count = dict()

    def handle_files(self) -> ['files']:
        ''' Adds all the files with uci.edu.txt
            in the current working directory to self.domains '''

        domains = { "ics.uci.edu","cs.uci.edu","informatics.uci.edu",
                    "stat.uci.edu","https://today.uci.edu/department/information_computer_sciences" }
        
        for f in os.listdir('.'):
            if os.path.isfile(f):
                if "uci.edu.txt" in f:
                    # self.domains includes the subdomains
                    self.domains.add(f)
                    if f not in domains:
                        self.subdomains[f.split('.txt')[0]] = 0
    

    def handle_domains(self):
        for f in self.domains:
            # variables to check if the current page is the longest page
            current_page = ""
            word_count = 0

            # To determine whether we should count the number of pages
            if f.split('.txt')[0] in self.subdomains:
                is_subdomain = True
            else:
                is_subdomain = False

            with open(f, "r") as text_file:
                for line in text_file:
                    # checking if the line is a page
                    if "uci.edu" in line:
                        curr_url = line
                        if "#" in line:
                            current_page = line.strip().split("#")[0]
                        else:
                            current_page = line.strip()
                        self.unique_pages.add(line.strip())
                        # If the current file open is a subdomain, increment
                        # the page by 1
                        if is_subdomain == True:
                            self.subdomains[f.split('.txt')[0]] += 1
                        
                    # signals the end of a page, so checks whether the 
                    # this was the longest page
                    if line == "STOPHERE\n":
                        if word_count > self.most_words:
                            self.most_words = word_count
                            self.longest_page = current_page
                            self.word_count[current_page] = self.most_words
                            self.most_words = 0
                            word_count = 0

                    else:
                        # the line is a word, so adds to the most common words
                        word = line.strip()
                        word_count += 1
                        if word in self.common_words:
                            self.common_words[word] += 1
                        else:
                            self.common_words[word] = 1
    

    def get_unique_pages(self):
        ''' returns the number of unique pages '''
        return len(self.unique_pages)
    
    def get_subdomains(self):
        ''' returns sorted list of subdomains '''
        return sorted(self.subdomains.items())

    def get_longest_page(self):
        ''' returns the page with most words on it '''
        self.word_count = sorted(self.word_count.items(),key=lambda x:x[1],reverse=True)
        self.word_count = list(self.word_count)
        return self.word_count[0][0]
    
    def get_longest_page_count(self):
        ''' returns longest page's word count '''
        return self.word_count[0][1]

    def get_common_words(self):
        ''' returns a list of the most common words
            and their respective word count '''
        most_common = []
        count = 0
        for k, v in sorted(self.common_words.items(), key = lambda x: x[1], reverse = True):
            if count < 50:
                most_common.append((k, v))
                count += 1
        return most_common

if __name__ == '__main__':
    p = Parser()
    p.handle_files()
    p.handle_domains()

    print("\nMost common words:")
    for x in p.get_common_words():
        print(x)

    print("\nSubdomain with number of unique pages sorted alphabetically:")
    for x in p.get_subdomains():
        print(x)
    
    print("\nUnique pages:", p.get_unique_pages())
    print("\nLongest Page: " + str(p.get_longest_page()) + "\tWord count: " + str(p.get_longest_page_count()))


'''
Deliverables: 
How many unique pages did you find? Uniqueness for the purposes of this assignment is ONLY established by the URL,
but discarding the fragment part. So, for example, http://www.ics.uci.edu#aaa and http://www.ics.uci.edu#bbb are the same URL. 
Even if you implement additional methods for textual similarity detection, please keep considering the above definition of unique 
pages for the purposes of counting the unique pages in this assignment.
What is the longest page in terms of number of words? (HTML markup doesn’t count as words)
What are the 50 most common words in the entire set of pages? Submit the list of common words ordered by frequency.
How many subdomains did you find in the ics.uci.edu domain? Submit the list of subdomains ordered alphabetically and the number of
unique pages detected in each subdomain. The content of this list should be lines containing URL, number, for example:
http://vision.ics.uci.edu, 10 (not the actual number here)
'''