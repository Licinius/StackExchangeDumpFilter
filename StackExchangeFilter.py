#!/usr/bin/env python
# coding: utf-8

import os
from ProgressBar import ProgressBar
try:
	import xml.etree.ElementTree as ET
	from lxml import etree
except ImportError:
	raise ImportError('Try: pip install lxml')

try:
	from bitarray import bitarray
except ImportError:
	raise ImportError('Try : pip install bitarray')
try:
	from file_read_backwards import FileReadBackwards
except ImportError:
	raise ImportError('Try : pip install file-read-backwards')
class StackExchangeFilter:
	'''
	Filter for StackExchange Dump
	Only filter : posts, votes, comments, postlinks, users and badges
	Attributes:
		POST_FILEPATH (str):		File path of the file containing posts	
		VOTES_FILEPATH (str):		File path of the file containing votes
		COMMENTS_FILEPATH (str):	File path of the file containing comments
		POSTLINKS_FILEPATH (str):	File path of the file containing post links
		USERS_FILEPATH (str):		File path of the file containing users
		BADGES_FILEPATH (str):		File path of the file containing badges
		
		filepath (str): 			File path of the folder containing the dump
		bitfield_posts (bitarray):	Bitfield of all the posts
		bitfield_users (bitarray):	Bitfield of all the users
	'''
	POSTS_FILEPATH = 'Posts.xml'
	VOTES_FILEPATH = 'Votes.xml'
	COMMENTS_FILEPATH = 'Comments.xml'
	POSTLINKS_FILEPATH = 'PostLinks.xml'
	USERS_FILEPATH = 'Users.xml'
	BADGES_FILEPATH = 'Badges.xml'

	def __init__(self,filepath,pretty_print = False):
		'''
		__init__ allows to set the file path of the dump folder and initialize
		the bitfields, they start at one to simplify the process
		bitfield_posts have a length of last_post_id + 1
		bitfield_users have a length of last_user_id + 1 and +1 for the community wiki where id = -1
		Args:
			filepath (str):	A filepath of the dump without the last separator

		'''
		self.filepath =  filepath if filepath.endswith(os.sep) else filepath + os.sep
		self.pretty_print = pretty_print
		index=0
		row = ""
		with FileReadBackwards(self.filepath + StackExchangeFilter.POSTS_FILEPATH, encoding="utf-8") as frb:
		    # getting lines by lines starting from the last line up
		    for i in range(2):
		    	row = frb.readline()
		row = ET.fromstring(row)
		self.last_post_id = int(row.attrib['Id'])
		#Id of the last Post to know the length of the bitfield
		self.bitfield_posts = bitarray(self.last_post_id+1)
		self.bitfield_posts.setall(False)
		#Id of the last User to know the length of the bitfield
		with FileReadBackwards(self.filepath + StackExchangeFilter.USERS_FILEPATH, encoding="utf-8") as frb:
		    for i in range(2):
		    	row = frb.readline()
		row = ET.fromstring(row)
		self.last_user_id = int(row.attrib['Id'])
		self.bitfield_users = bitarray(self.last_user_id+2) #For Community wiki need one more cell
		self.bitfield_users.setall(False)

		with FileReadBackwards(self.filepath + StackExchangeFilter.COMMENTS_FILEPATH, encoding="utf-8") as frb:
		    for i in range(2):
		    	row = frb.readline()
		row = ET.fromstring(row)
		self.last_comment_id = int(row.attrib['Id'])


		with FileReadBackwards(self.filepath + StackExchangeFilter.BADGES_FILEPATH, encoding="utf-8") as frb:
		    for i in range(2):
		    	row = frb.readline()
		row = ET.fromstring(row)
		self.last_badge_id = int(row.attrib['Id'])

		with FileReadBackwards(self.filepath + StackExchangeFilter.VOTES_FILEPATH, encoding="utf-8") as frb:
		    for i in range(2):
		    	row = frb.readline()
		row = ET.fromstring(row)
		self.last_vote_id = int(row.attrib['Id'])

		with FileReadBackwards(self.filepath + StackExchangeFilter.POSTLINKS_FILEPATH, encoding="utf-8") as frb:
		    for i in range(2):
		    	row = frb.readline()
		row = ET.fromstring(row)
		self.last_postlink_id = int(row.attrib['Id'])

	def __set_bitfield_users(self,row):
		'''
		This function is fired to set the bitfield_user when the program encounter a post
		Args:
			row (_Element):	A row of post
		Returns:
			The updated bitfield of user
		'''
		owner_user_id = row.attrib.get('OwnerUserId')
		if(owner_user_id is not None):
			owner_user_id = int(owner_user_id)
			self.bitfield_users[owner_user_id] = True

		last_editor_user_id = row.attrib.get('LastEditorUserId')
		if(last_editor_user_id is not None):
			last_editor_user_id = int(last_editor_user_id)
			self.bitfield_users[last_editor_user_id] = True

		user_id = row.attrib.get('UserId')
		if(user_id is not None):
			user_id = int(user_id)
			self.bitfield_users[user_id] = True
		return self.bitfield_users
	def posts(self,main_tag,extras_tags,minimum_answers=0):
		'''
		This function will filter the posts of the dump like this
			\\row[contains(@Tags,'<mainTag>')
				and @AnswersCount >= minimum_answers
				and (contains(@Tags,'<extras_tags[0]>')
					or contains(@Tags,'<extras_tags[1]>')
					...
					or contains(@Tags,'<extras_tags[n]>')
				)]
		Args : 
			main_tag (str) :		The tag required in the query 
			extras_tags (array) :	The optionals tags in the query
			minimum_answers (int) :	The minimum number of answers of a question (default=0)

		Returns : 
			self (StackExchangeFilter) : 	The current object
		'''
		root_name = 'posts'
		main_filter=''
		if(main_tag is not None):
			main_filter = 'contains(@Tags,"<%s>") and ' % main_tag
		extras_filters = ''
		first=True
		if(extras_tags is not None):
			extras_filters = ' and ('
			for tag in extras_tags : 
				if(first!=True):
					extras_filters +=' or '
				else :
					first = False
				extras_filters += ' contains(@Tags,"<%s>") ' %tag
			extras_filters += ') '


		question_path = 'self::*[%s @AnswerCount>=%s %s ]' %(main_filter,minimum_answers,extras_filters)
		output_path = 'output/%s'% StackExchangeFilter.POSTS_FILEPATH
		with open(output_path,'w') as output:
			output.write('<%s>' %root_name)
			progressbar = ProgressBar(self.last_post_id, prefix = 'Progress:', suffix = 'Complete', length = 50)
			try:
				for event, row in etree.iterparse(self.filepath + StackExchangeFilter.POSTS_FILEPATH, tag='row'):
					row_id = int(row.attrib['Id'])
					if(self.pretty_print): #Display the progress only if the user wanted to
						progressbar.printProgressBar(row_id)
					if (row.xpath(question_path)):
						self.__set_bitfield_users(row)
						self.bitfield_posts[row_id] = True
						output.write(etree.tostring(row,pretty_print=True).decode('utf-8'))
					else:
						parent_id = row.attrib.get('ParentId')
						if(parent_id is not None):
							if(self.bitfield_posts[int(parent_id)]):
								self.bitfield_posts[row_id] = True
								self.__set_bitfield_users(row)
								output.write(etree.tostring(row,pretty_print=True).decode('utf-8'))
					row.clear()
			except FileNotFoundError:
				print('Invalid filepath : %s' %self.filepath + StackExchangeFilter.POSTS_FILEPATH)
				exit(1)
			output.write('</%s>' %root_name)
		return self

	def votes(self):
		'''
		This function will be fired to retrieve the votes corresponding to the selected posts in the function posts
		Returns :
			self (StackExchangeFilter) : The current object
		'''
		root_name = 'votes'
		output_path = 'output/%s'%   StackExchangeFilter.VOTES_FILEPATH
		with open(output_path,'w') as output:
			output.write('<%s>' %root_name)
			progressbar = ProgressBar(self.last_vote_id, prefix = 'Progress:', suffix = 'Complete', length = 50)
			try:
				for event, row in etree.iterparse(self.filepath + StackExchangeFilter.VOTES_FILEPATH,tag='row'):
					post_id = int(row.attrib['PostId'])
					if(self.pretty_print): #Display the progress only if the user wanted to
						progressbar.printProgressBar(int(row.attrib['Id']))
					if (self.bitfield_posts[post_id]):
						self.__set_bitfield_users(row)
						output.write(etree.tostring(row,pretty_print=True).decode('utf-8'))
					row.clear()
			except FileNotFoundError:
				print('Please check if the dump of "vote" is present in the filepath')
				exit(1)
			output.write('</%s>' %root_name)
		return self


	def comments(self):
		'''
		This function will be fired to retrieve the comments corresponding to the selected posts in the function posts
		Returns :
			self (StackExchangeFilter) : The current object
		'''
		root_name = 'comments'
		output_path = 'output/%s'%   StackExchangeFilter.COMMENTS_FILEPATH
		with open(output_path,'w') as output:
			output.write('<%s>' %root_name)
			try:
				progressbar = ProgressBar(self.last_comment_id, prefix = 'Progress:', suffix = 'Complete', length = 50)
				for event, row in etree.iterparse(self.filepath + StackExchangeFilter.COMMENTS_FILEPATH,tag='row'):
					post_id = int(row.attrib['PostId'])
					if(self.pretty_print): #Display the progress only if the user wanted to
						progressbar.printProgressBar(int(row.attrib['Id']))
					if (self.bitfield_posts[post_id]):
						self.__set_bitfield_users(row)
						output.write(etree.tostring(row,pretty_print=True).decode('utf-8'))
					row.clear()
			except FileNotFoundError:
				print('Please check if the dump of "comments" is present in the filepath')
				exit(1)
			output.write('</%s>' %root_name)
		return self

	def postLinks(self):
		'''
		This function will be fired to retrieve the postlinks corresponding to the selected posts in the function posts
		Returns :
			self (StackExchangeFilter) : The current object
		'''
		root_name = 'postlinks'
		output_path = 'output/%s'%   StackExchangeFilter.POSTLINKS_FILEPATH
		with open(output_path,'w') as output:
			output.write('<%s>' %root_name)
			try:
				progressbar = ProgressBar(self.last_postlink_id, prefix = 'Progress:', suffix = 'Complete', length = 50)
				for event, row in etree.iterparse(self.filepath + StackExchangeFilter.POSTLINKS_FILEPATH,tag='row'):
					post_id = int(row.attrib['PostId'])
					if(self.pretty_print):
						progressbar.printProgressBar(int(row.attrib['Id']))
					related_post_id = int(row.attrib['RelatedPostId'])
					if (self.bitfield_posts[post_id] or self.bitfield_posts[related_post_id]):
						output.write(etree.tostring(row,pretty_print=True).decode('utf-8'))
					row.clear()
			except FileNotFoundError:
				print('Please check if the dump of "postlinks" is present in the filepath')
				exit(1)
			output.write('</%s>' %root_name)
		return self

	def users(self):
		'''
		This function will be fired to retrieve the users corresponding to the selected users while browsing the post
		and comments
		Returns :
			self (StackExchangeFilter) : The current object
		'''
		root_name = 'users'
		output_path = 'output/%s'%   StackExchangeFilter.USERS_FILEPATH
		with open(output_path,'w') as output:
			output.write('<%s>' %root_name)
			progressbar = ProgressBar(self.last_user_id, prefix = 'Progress:', suffix = 'Complete', length = 50)
			try:
				for event, row in etree.iterparse(self.filepath + StackExchangeFilter.USERS_FILEPATH,tag='row'):
					user_id = int(row.attrib['Id'])
					if(self.pretty_print and user_id>0):
						progressbar.printProgressBar(user_id)
					if (self.bitfield_users[user_id]):
						output.write(etree.tostring(row,pretty_print=True).decode('utf-8'))
					row.clear()
			except FileNotFoundError:
				print('Please check if the dump of "users" is present in the filepath')
				exit(1)
			output.write('</%s>' %root_name)
		return self

	def badges(self):
		'''
		This function will be fired to retrieve the badges owned by the users selected
		Returns :
			self (StackExchangeFilter) : The current object
		'''
		root_name = 'badges'
		output_path = 'output/%s'%   StackExchangeFilter.BADGES_FILEPATH
		with open(output_path,'w') as output:
			output.write('<%s>' %root_name)
			try:
				progressbar = ProgressBar(self.last_badge_id, prefix = 'Progress:', suffix = 'Complete', length = 50)
				for event, row in etree.iterparse(self.filepath + StackExchangeFilter.BADGES_FILEPATH,tag='row'):
					user_id = int(row.attrib['UserId'])
					if(self.pretty_print):
						progressbar.printProgressBar(int(row.attrib['Id']))
					if (self.bitfield_users[user_id]):
						output.write(etree.tostring(row,pretty_print=True).decode('utf-8'))
					row.clear()
			except Exception:
				print('Please check if the dump of "badges" is present in the filepath')
				exit(1)
			output.write('</%s>' %root_name)
		return self