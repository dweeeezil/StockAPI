class ProgressBar:
    def __init__(self,
                 barLength:int = 100,
                 label:str = 'Progress:',):

        self.current = 0
        self.barLength = barLength
        self.label = label
        self.progress = 0

    def show(self):
        print(f'{self.label}', end='\r', flush=True)

    def update(self, current, logging:bool = True): #current = current progress normalized 0-1
        current *= self.barLength
        tail = (' ' * int(round(self.barLength - current) - 1)) + ']'
        bars = '' + ('|' * int(round(current)))
        percentTag = f'{round(current) + 1}%'

        if logging:
            print(f'{self.label}[{bars}{tail} - {percentTag}', end='\r', flush=True)

        if round(current) + 1 == 100 and logging:
            print(f'\nDone')

        return f'{self.label}[{bars}{tail} - {percentTag}'