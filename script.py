import argparse
from filters.StackExchangeFilter import StackExchangeFilter
#Initialize argparse for argument to parse
parser = argparse.ArgumentParser(description='Filter Post.xml of StackOverflow')
parser.add_argument('filepath', metavar='filepath', type=str,
                    help='The filepath of the Posts.xml')
parser.add_argument('-mt','--mainTag',metavar="mainTag",nargs="?",help="A main tag to filter",default=None)
parser.add_argument('-et','--extrasTags',metavar="extrasTags",nargs="*",help="Extras tags to filter",default=None)
parser.add_argument('-ma','--minimumAnswers',metavar="minimumAnswers",type=int,nargs="?",help="Number of minimumAnswers of each question, default=0",default=0)
args = parser.parse_args()

##Start script##
print('Start')
filter = StackExchangeFilter(args.filepath)

print('Extract posts')
filter.posts(args.mainTag,args.extrasTags,args.minimumAnswers)
print('Extract votes')
filter.votes()
print('Extract comments')
filter.comments()
print('Extract Posts links')
filter.postLinks()
print('Extract Users')
filter.users()
print('Extract Badges')
filter.badges()
print('Done')
exit(0)