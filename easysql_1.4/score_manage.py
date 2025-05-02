from os import path as p
import json

class score_manage():
    def __init__(self)->None:
        self.Totalmarks = 10
        self.filename = "scores.json"
        if not p.exists(self.filename):
            with open(self.filename,'w') as f:
                json.dump({}, f)
                ...

    def updateScore(self:None, token:str)->None:
        scores = dict()
        with open(self.filename,"r") as f:
            score = f.read()
            if score:
                scores = json.loads(score)

        #print(f"score: {scores}")
        #if token is not presnt then assign a dummy score half of full marks
        if token not in scores.keys():
            scores[token] = self.Totalmarks/2
        else:
            #print(f"score[token] : {type(scores[token])}")
            #scores[token] = (scores[token] + len(scores)/self.Totalmarks) % self.Totalmarks
            scores[token] = min(self.Totalmarks, scores[token] + 0.1)
            ...
        
        for key in scores.keys():
            if key != token:
                scores[key] = max(0, scores[key] - 0.1)  # Decrease but not go below 0


        with open(self.filename,"w") as f:
            f.write(json.dumps(scores))
        

    def showScore(self:None, token:str)->float:
        ...
    
    def increaseScore(self:None, token:str)->None:
        #increase the token score by 0.2 if possible else assign 10
        ...
    
    def decreaseScore(self:None, token:str)->None:
        #decrease the token score by 0.2 if possible else assign 0
        ...


    def getScore(self:None)->dict[str:float]:
        with open(self.filename, "r") as f:
            score = f.read()
            if score:
                return json.loads(score)
        return {}
        ...

    def arrangeSuggestions(self:None, suggestions:list[str])->list[str]:
        scores = self.getScore()
        return sorted(suggestions, key=lambda x: scores.get(x, 0), reverse=True)
        ...
    
'''
ob = score_manage()
suggestions= ['[TABLE];', '[FIELD3]', 'CASE', 'avengers', '(SELECT', 'student']
suggestions = [token.upper() for token in suggestions]
while True:
    #user_input = input("Enter token : ").upper()
    #suggestions.append(user_input)
    #ob.updateScore(user_input)
    print(ob.getScore())
    print(ob.arrangeSuggestions(suggestions))
    input()
'''