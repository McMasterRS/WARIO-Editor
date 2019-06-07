from consecution import Pipeline, Node, GroupByNode

class SimpleNode(Node):
    def process(self, item):
        print('{} processing {}'.format(self.name, item))
        self.push(item)

class OutputNode(Node):
    def process(self, item):
        print('{} processing {}'.format(self.name, item))
        print()
        self.push(item)

class TopNode(Node):
    def process(self, item):
        print()
        print('{} processing {}'.format(self.name, item))
        print()
        self.push(item)


class OtherNodeA(Node):
    def process(self, item):
        #self.item = self.item * 2
        print('{} processing {}'.format(self.name, item))
        self.push(item + 1)

class OtherNodeB(Node):
    def process(self, item):
        #self.item = self.item * 2
        print('{} processing {}'.format(self.name, item))
        self.push(item + 5)

class MergeNode(Node):
    def begin(self):
        self.pair = []
        #self.gps
        #self.acc
    def process(self, item):
        self.pair.append(item)
        print('{} processing {}'.format(self.name, item))
        if (len(self.pair) == 2):
            temp = self.pair.copy()
            print('pair: ',end='')
            print(self.pair)
            self.pair.clear()
            self.push(sum(temp))



'''
class BatchNode(GroupByNode):
    def begin(self):
        self.counter = 0
        self.items = 0

    def key(self, item):
        print('batch: ',end='')
        print(self._batch_, end=' - counter: ')
        print(self.counter)
        return self.counter // 2

    def process(self, batch):
        print(batch)
        self._batch_ = ''
        self.push(batch)
'''

top = TopNode('top')

leftA = SimpleNode('leftA')
rightA = OtherNodeA('rightA')
mergeA = MergeNode('mergeA')
outputA = OutputNode('outputA')


leftB = SimpleNode('leftB')
rightB = OtherNodeB('rightB')
mergeB = MergeNode('mergeB')
outputB = OutputNode('outputB')

top.add_downstream(leftA)
top.add_downstream(rightA)
top.add_downstream(leftB)
top.add_downstream(rightB)

leftA.add_downstream(mergeA)
rightA.add_downstream(mergeA)

leftB.add_downstream(mergeB)
rightB.add_downstream(mergeB)

mergeA.add_downstream(outputA)
mergeB.add_downstream(outputB)

#alpha = SimpleNode('alpha')
#beta = SimpleNode('beta')
#top.add_downstream(left)
#top.add_downstream(right)

#left.add_downstream(output)
#right.add_downstream(output)
#blat = alpha | beta


#print(type(node_object))

pipe = Pipeline(top)
print(pipe)
pipe.plot('plot.png','png')
pipe.consume(range(4))
