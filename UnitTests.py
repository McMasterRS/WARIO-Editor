from unittest import TestCase, TestSuite, main
from pipeline.Pipeline import Pipeline
from pipeline.Node import Node

class TestPipeline(TestCase):
    def setUp(self):
        self.pipeline = Pipeline()
        self.root_a = MockRootNode('root a')
        self.root_b = Node("root b")
        self.root_C = Node("root c")

        self.middle_a = MockMiddleNode("middle a")
        self.middle_b = MockMiddleNode("middle b")
        self.middle_c = MockMiddleNode("middle c")

        self.leaf_a = MockLeafNode("leaf a")
        self.leaf_b = MockLeafNode("leaf b")
        self.leaf_c = MockLeafNode("leaf c")

    def test_add(self):
        """ Test adding Nodes """
        node = Node("ID")
        self.pipeline.add(node)
        self.assertIn(node, self.pipeline.nodes)
        self.assertIn(node, self.pipeline.roots)

    def test_single_connect(self):
        """ Connecting Two Nodes """
        parent_terminal, child_terminal, child = self.pipeline.connect((self.root_a, 'OUT'), (self.leaf_a, 'IN'))
        self.assertEqual(parent_terminal, 'OUT')
        self.assertEqual(child_terminal, 'IN')
        self.assertEqual(child, self.leaf_a)
        self.assertEqual((parent_terminal, child_terminal, child), self.pipeline.nodes[self.root_a][-1])

    def test_run_with_child(self):
        """ Test run a node that has a single child and no parents """
        self.pipeline.connect((self.root_a, "OUT"), (self.middle_a, "IN"))
        results, done = self.pipeline.run_node(self.root_a)
        print(results[self.root_a]['OUT'])
        self.assertEqual(results[self.root_a]['OUT'], 1)
        self.assertEqual(results[self.middle_a]['OUT'], 2)

    def test_run_with_children(self):
        """ Test run a node with both children and parents """
        self.pipeline.connect((self.root_a, "OUT"), (self.middle_a, "IN"))
        self.pipeline.connect((self.root_a, "OUT"), (self.middle_b, "IN"))
        results, done = self.pipeline.run_node(self.root_a)
        self.assertEqual(results[self.root_a]['OUT'], 1)
        self.assertEqual(results[self.middle_a]['OUT'], 2)
        self.assertEqual(results[self.middle_b]['OUT'], 2)

class MockRootNode(Node):
    def process(self):
        return {
            "OUT": 1
        }

class MockMiddleNode(Node):
    def process(self):
        return {
            'OUT': self.args["IN"] + 1
        }

class MockLeafNode(Node):
    def process(self):
        print (self.args["IN"])

class MockEventListenerNode(Node):
    def process(self):
        print (self.args["IN"])
        self.event_callbacks = self.event_callback
        return {
            "OUT": self.args["IN"]
        }

    def event_callback(self):
        print("EVENT RECIEVED")

class MockEventTriggerNOde(Node):
    def process(self):
        self.events_fired = {
            "MOCK EVENT"
        }

class MockBatchNode(Node):
    def start(self):
        self.values = [0,1,2,3,4,5,6,7]

    def process(self):
        return self.next_value()

    def next_value(self):
        return self.values.pop()


if __name__ == '__main__':
    main()