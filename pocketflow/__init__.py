import warnings, copy, time

class BaseNode:
    def __init__(self): self.params,self.successors={},{}
    def set_params(self,params): self.params=params
    def add_successor(self,node,action="default"):
        if action in self.successors: warnings.warn(f"Overwriting successor for action '{action}'")
        self.successors[action]=node;return node
    def prep(self,shared): pass
    def exec(self,prep_res, shared): pass
    def post(self,shared,prep_res,exec_res): pass
    def _exec(self,prep_res, shared): return self.exec(prep_res, shared)
    def _run(self,shared): p=self.prep(shared);e=self._exec(p, shared);return self.post(shared,p,e)
    def run(self,shared):
        if self.successors: warnings.warn("Node won't run successors. Use Flow.")
        return self._run(shared)
    def __rshift__(self,other): return self.add_successor(other)
    def __sub__(self,action):
        if isinstance(action,str): return _ConditionalTransition(self,action)
        raise TypeError("Action must be a string")

class _ConditionalTransition:
    def __init__(self,src,action): self.src,self.action=src,action
    def __rshift__(self,tgt): return self.src.add_successor(tgt,self.action)

class Node(BaseNode):
    def __init__(self,max_retries=1,wait=0): super().__init__();self.max_retries,self.wait=max_retries,wait
    def exec_fallback(self,prep_res,exc, shared): raise exc
    def _exec(self,prep_res, shared):
        for self.cur_retry in range(self.max_retries):
            try: return self.exec(prep_res, shared)
            except Exception as e:
                if self.cur_retry==self.max_retries-1: return self.exec_fallback(prep_res,e, shared)
                if self.wait>0: time.sleep(self.wait)

class BatchNode(Node):
    def _exec(self,items, shared): return [super(BatchNode,self)._exec(i, shared) for i in (items or [])]

class Flow(BaseNode):
    def __init__(self,start): super().__init__();self.start=start
    def get_next_node(self,curr,action):
        nxt=curr.successors.get(action or "default")
        if not nxt and curr.successors: warnings.warn(f"Flow ends: '{action}' not found in {list(curr.successors)}")
        return nxt
    def _orch(self,shared,params=None):
        curr,p=copy.copy(self.start),(params or {**self.params})
        while curr: curr.set_params(p);c=curr._run(shared);curr=copy.copy(self.get_next_node(curr,c))
    def _run(self,shared): pr=self.prep(shared);self._orch(shared);return self.post(shared,pr,None)
    def exec(self,prep_res, shared): raise RuntimeError("Flow can't exec.")

class BatchFlow(Flow):
    def _run(self,shared):
        pr=self.prep(shared) or []
        for bp in pr: self._orch(shared,{**self.params,**bp})
        return self.post(shared,pr,None)
