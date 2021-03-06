import ui,sqlite3,datetime,sound,console

# I'd like to add a timestamp to notes, so:
time_stamp = datetime.datetime.today().strftime('%m_%d_%Y_%H:%M:%S')
# File name for our notes file (here for easy accesss)
save_file = 'notes.txt'
# File name for our thoughts file.
thoughts_file = 'thoughts.txt'

def updates(*args):
	# Connect to the swlite database and create a cursor to query it with
	con = sqlite3.connect('bible-sqlite.db')
	cursor=con.cursor()
	# Three argument parameters (all tanleviews) that were passed in using a lambda function.
	tbl_books = args[0]
	tbl_chapters = args[1]
	tbl_testaments = args[2]
	
	# A query to get all book names in the 'key_english' table
	all_bks_query = 'select n from key_english'
	all_bks = [x[0] for x in cursor.execute(all_bks_query)]
	
	# A query to get all old testament book names in the 'key_english' table 
	ot_query = 'select n from key_english where b < 40'
	ot_bks = [x[0] for x in cursor.execute(ot_query)]
	
	# A query to get all new testament book names in the 'key_english' table 
	nt_query = 'select n from key_english where b > 40'
	nt_bks = [x[0] for x in cursor.execute(nt_query)]
	
	# Set the 'books' table's items to all books of the bible
	tbl_books.items = all_bks
	# Store tableview selections
	selected_book = tbl_books.items[tbl_books.selected_row]
	selected_chap = tbl_chapters.items[tbl_chapters.selected_row]
	selected_testament = tbl_testaments.items[tbl_testaments.selected_row]

	#if selected_testament=='Old Testament':
		#tbl_books.items=ot_bks
	
	#elif selected_testament=='New Testament':
		#tbl_books.items= nt_bks
	
	# Select book from the key_english table where the name = the selected book/cell of a tableview
	num_query = "select b from key_english where n='{}'".format(selected_book)
	bk_num=[x for x in cursor.execute(num_query)][0][0]
	
	c = selected_chap # uneccesary perhaps but using 'c' is shorter.
	
	# Select chapter,verse,text from the t-kjv table where book = book number (tableview) and chapter = selected chapter
	txt_query = "select c,v,t from 't_kjv' where b = '{}' AND c = '{}'".format(bk_num,c)
	txt = [row for row in cursor.execute(txt_query)]
	# Format the text as -- ''+chapter+text -- ('' can be replaced with whatever prefix you want)
	txt_formatted = "\n".join("{} {}: {}\n".format('',c,t) for b,c,t in txt)
	
	# If the formatted text is an empty string, set the contents textview to a string
	# This is a quick fix if a user selects a chapter in a book that doesnt exist for that book
	if txt_formatted=='':
		contents.text = 'Chapter does not exist'
	
	# Otherwise, set the contents textview to the formatted text
	else: contents.text = txt_formatted
	# Set the heading label to the selected book plus the selected chapter (as a string)
	heading.text=selected_book+' '+str(selected_chap)

def save_selection(sender):
	'''saves the selected text in a textview to a file. If no text is selected, the entire text is saved.'''
	# Get the beginning of the textview selection
	beg= contents.selected_range[0]
	# Get the end of the textview selection
	end = contents.selected_range[1]
	# Get the entire text in the textview
	txt = contents.text
	# If text is selected (if there is a substring from beginning to end)...
	with open(save_file,'a') as outfile:
		if txt[beg:end] != '':
			# write the text to a file with a timestamp, the heading lable text, and the selected text.
			outfile.write('\n'+time_stamp+'\n'+heading.text+'\n\n'+txt[beg:end]+'\n')
		# Otherwise...
		else:
			# write the entire text to the file.
			outfile.write('\n'+time_stamp+'\n'+heading.text+'\n\n'+txt+'\n')
	# Play a sound
	sound.play_effect('ui:switch8')
	# Alert the user that fhe file has been saved to the file.
	console.alert('Saved to {}'.format(save_file))

# Same logic as save_selection
def selectionToThoughts(sender):
	beg= contents.selected_range[0]
	end = contents.selected_range[1]
	txt = contents.text
	if txt[beg:end] != '':
		thoughts.text = thoughts.text +heading.text+'\n'+txt[beg:end]+'\n\n'
	else:
		thoughts.text = thoughts.text +heading.text+'\n'+txt+'\n\n'
	sound.play_effect('rpg:DrawKnife2')

def save_thoughts(sender):
	with open(thoughts_file,'a')	as outfile:
		outfile.write(time_stamp+'\n'+thoughts.text+'\n')
	sound.play_effect('rpg:BookFlip2')
	console.alert('Saved to {}'.format(thoughts_file))

# Make a textview editable or not editable with a switch.
def freeze(sender):
	if sender.value == True:
		thoughts.editable=True
	if sender.value==False:
		thoughts.editable=False

# Load text from a file into the 'thoughts' textview
def load_thoughts(sender):
	with open(thoughts_file,'r') as infile:
		thoughts.text = infile.read()

# Set the 'thoughts' textview to an empty string (clear it).
def clear_thoughts(sender):
	thoughts.text=''

# Creating a quick popup sheet to preview a text file called 'thoughts.txt' (see top)
def view_thoughts(sender):
	v=ui.View()
	v.width=540
	v.height=540
	v.background_color='white'
	tv=ui.TextView()
	tv.width=v.width
	tv.height=v.height
	tv.background_color=''
	tv.editable=False
	tv.font=('Times New Roman',18)
	with open(thoughts_file,'r') as infile:
		tv.text=infile.read()
	v.add_subview(tv)
	v.present('sheet')


# IMPLEMENTATION
# Getting ui elements and setting actions
bible = ui.load_view()
heading = bible['book_heading']
books = bible['books']
chapters = bible['chapters']
contents = bible['contents']
testaments = bible['testaments']
thoughts = bible['view1']['thought_bubble']
thoughts_switch = bible['view1']['switch']
thoughts_switch.action = freeze
thoughts_button = bible['view1']['btn_thoughts']
thoughts_button.action = selectionToThoughts
thoughts_save_button = bible['view1']['btn_save_thoughts']
thoughts_save_button.action = save_thoughts
load_button = bible['view1']['btn_load']
load_button.action = load_thoughts
clear_button = bible['view1']['btn_clear']
clear_button.action=clear_thoughts
save_button = bible['view1']['btn_save']
save_button.action=save_selection

# Peloading text into a textview called 'thoughts'
with open('instructions.txt','r') as infile:
	thoughts.text = infile.read()

# This lambda function is what allows me to pass arguments to a view's action function. This function is what makes it all work.
f = lambda sender: updates(sender,chapters.data_source,testaments.data_source)

# Quick and dirty query to preload a tableview with an sqlite record.
books.data_source.items = [x[0] for x in sqlite3.connect('bible-sqlite.db').execute('select n from key_english')]
books.data_source.action = f

# Display the bible and restrict its orientation to landscape.
bible.present(orientations=['landscape'])
