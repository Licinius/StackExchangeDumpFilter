import os
try:
	from lxml import etree
except ImportError:
	raise ImportError("Try: pip install lxml")

try:
	from bitarray import bitarray
except ImportError:
	raise ImportError("Try : pip install bitarray")

class StackExchangeFilter:
	'''
		Filter for StackExchange Dump
		Only filter : posts, votes, comments, postlinks, users and badges

	'''
	POSTS_FILEPATH = "Posts.xml"
	VOTES_FILEPATH = "Votes.xml"
	COMMENTS_FILEPATH = "Comments.xml"
	POSTLINKS_FILEPATH = "PostLinks.xml"
	USERS_FILEPATH = "Users.xml"
	BADGES_FILEPATH = "Badges.xml"

	def __init__(self,filepath):
		self.filepath = filepath + os.sep
		#Id of the last Post to know the lenght of the bitfield
		tree_posts = etree.parse(self.filepath+__class__.POSTS_FILEPATH)
		last_post_id = int(tree_posts.xpath("(//row)[last()]")[0].attrib['Id'])
		self.bitfield_posts = bitarray(last_post_id+1)
		self.bitfield_posts.setall(False)
		#Id of the last User to know the lenght of the bitfield
		tree_users = etree.parse(self.filepath+__class__.USERS_FILEPATH)
		last_user_id = int(tree_users.xpath("(//row)[last()]")[0].attrib['Id'])
		self.bitfield_users = bitarray(last_user_id+2) #For Community wiki need one more cell
		self.bitfield_users.setall(False)

	def __set_bitfield_users(self,row):
		owner_user_id = row.attrib.get('OwnerUserId')
		if(owner_user_id is not None):
			owner_user_id = int(owner_user_id)
			self.bitfield_users[owner_user_id] = True

		last_editor_user_id = row.attrib.get('LastEditorUserId')
		if(last_editor_user_id is not None):
			last_editor_user_id = int(last_editor_user_id)
			self.bitfield_users[last_editor_user_id] = True

	def posts(self,main_tag,extras_tags,minimum_answers=0):
		try:
			tree = etree.parse(self.filepath+__class__.POSTS_FILEPATH)
		except Exception:
			print("Invalid filepath : %s" %self.filepath+__class__.POSTS_FILEPATH)
			exit(-1)

		root_name = "posts"

		main_filter=""
		if(main_tag is not None):
			main_filter = 'contains(@Tags,"<%s>") and ' % main_tag
		extras_filters = ""
		first=True
		if(extras_tags is not None):
			extras_filters = " and ("
			for tag in extras_tags : 
				if(first!=True):
					extras_filters +=" or "
				else :
					first = False
				extras_filters += " contains(@Tags,'<%s>') " %tag
			extras_filters += ") "


		path = '//row[%s @AnswerCount>=%s %s ]' %(main_filter,minimum_answers,extras_filters)
		output_path = 'output/%s'% __class__.POSTS_FILEPATH
		with open(output_path,'w') as output:
			output.write("<%s>" %root_name)
			for row in tree.xpath(path):
				row_id = int(row.attrib['Id'])
				self.__set_bitfield_users(row)
				self.bitfield_posts[row_id] = True
				output.write(etree.tostring(row,pretty_print=True).decode("utf-8"))
				possible_answers = row.xpath("following-sibling::*[@ParentId='%s']" %row.attrib['Id'])
				for answer in possible_answers:
					answer_id = int(answer.attrib['Id'])
					self.bitfield_posts[answer_id] = True
					self.__set_bitfield_users(answer)
					output.write(etree.tostring(answer,pretty_print=True).decode("utf-8"))
			output.write("</%s>" %root_name)

	def votes(self):
		try:
			tree_votes = etree.parse(self.filepath+__class__.VOTES_FILEPATH)
		except Exception:
			print("Error, vote")
			exit(-1)
		root_name = 'votes'
		output_path = 'output/%s'% __class__.VOTES_FILEPATH
		with open(output_path,'w') as output:
			output.write("<%s>" %root_name)
			for row in tree_votes.xpath('//row'):	
				postId = int(row.attrib['PostId'])
				if (self.bitfield_posts[postId]):
					output.write(etree.tostring(row,pretty_print=True).decode("utf-8"))
			output.write('</%s>' %root_name)


	def comments(self):
		try:
			tree_comments = etree.parse(self.filepath+__class__.COMMENTS_FILEPATH)
		except Exception:
			print("Error, comments")
			exit(-1)
		root_name = "comments"
		output_path = 'output/%s'% __class__.COMMENTS_FILEPATH
		with open(output_path,'w') as output:
			output.write("<%s>" %root_name)
			for row in tree_comments.xpath("//row"):
				postId = int(row.attrib['PostId'])
				if (self.bitfield_posts[postId]):
					output.write(etree.tostring(row,pretty_print=True).decode("utf-8"))
			output.write("</%s>" %root_name)

	def postLinks(self):
		try:
			tree_postLinks = etree.parse(self.filepath+__class__.POSTLINKS_FILEPATH)
		except Exception:
			print("Error, postlinks")
			exit(-1)
		root_name = "postlinks"
		output_path = 'output/%s'% __class__.POSTLINKS_FILEPATH
		with open(output_path,'w') as output:
			output.write("<%s>" %root_name)
			for row in tree_postLinks.findall("row"):
				post_id = int(row.attrib['PostId'])
				related_post_id = int(row.attrib['RelatedPostId'])
				if (self.bitfield_posts[post_id] or self.bitfield_posts[related_post_id]):
					output.write(etree.tostring(row,pretty_print=True).decode("utf-8"))
			output.write("</%s>" %root_name)

	def users(self):
		try:
			tree_users = etree.parse(self.filepath+__class__.USERS_FILEPATH)
		except Exception:
			print("Error, users")
			exit(-1)
		root_name = "users"
		output_path = 'output/%s'% __class__.USERS_FILEPATH
		with open(output_path,'w') as output:
			output.write("<%s>" %root_name)
			for row in tree_users.xpath('//row'):
				# if the id of the row is present in at least one post
				user_id = int(row.attrib['Id'])
				if (self.bitfield_users[user_id]):
					output.write(etree.tostring(row,pretty_print=True).decode("utf-8"))
			output.write("</%s>" %root_name)

	def badges(self):
		try:
			tree_badges = etree.parse(self.filepath+__class__.BADGES_FILEPATH)
		except Exception:
			print("Error, badges")
			exit(-1)
		root_name = 'badges'
		output_path = 'output/%s'% __class__.BADGES_FILEPATH
		with open(output_path,'w') as output:
			output.write("<%s>" %root_name)
			for row in tree_badges.xpath('//row'):		

				user_id = int(row.attrib['UserId'])		
				if (self.bitfield_users[user_id]):
					output.write(etree.tostring(row,pretty_print=True).decode("utf-8"))
			output.write('</%s>' %root_name)