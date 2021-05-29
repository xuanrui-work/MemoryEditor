from .MemoryEditor import MemoryEditor

class MemoryLocationDirect:
	def __init__(self, memoryEditor: MemoryEditor, baseAddress, ctype):
		self.me = memoryEditor
		self.baseAddress = baseAddress
		self.ctype = ctype

	def read(self):
		return self.me.readData(self.baseAddress, self.ctype)

	def write(self, value):
		return self.me.writeData(self.baseAddress, self.ctype, value)

class MemoryLocationIndirect:
	def __init__(self, memoryEditor: MemoryEditor, baseAddress, offsets, ctype):
		self.me = memoryEditor
		self.baseAddress = baseAddress
		self.offsets = offsets
		self.ctype = ctype

	def read(self):
		pointer = self.me.tracePointer(self.baseAddress, self.offsets)
		return self.me.readData(pointer, self.ctype)

	def write(self, value):
		pointer = self.me.tracePointer(self.baseAddress, self.offsets)
		return self.me.writeData(pointer, self.ctype, value)
