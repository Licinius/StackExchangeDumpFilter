class ProgressBar():
    '''
    Class inspire by https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    '''
    def __init__(self, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
        """
        Call before the loop to initialize the progress bar
        Args:
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
        """

        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.length = length
        self.fill = fill
    def printProgressBar (self,iteration):
        '''
        Call in a loop to create terminal progress bar
        Args:
            iteration   - Required  : current iteration (Int)
        '''
        filled_length = int(self.length * iteration // self.total)
        bar = self.fill * filled_length + '-' * (self.length - filled_length)
        percent = ("{0:." + str(self.decimals) + "f}").format(100 * (iteration / float(self.total)))
        print('\r%s |%s| %s%% %s' % (self.prefix, bar, percent, self.suffix), end = '\r')
        # Print New Line on Complete
        if iteration == self.total: 
            print()