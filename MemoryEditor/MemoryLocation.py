from .MemoryEditor import MemoryEditor

class MemoryLocationDirect:
	"""
	The MemoryLocationDirect class is used to represent a memory location to be accessed directly,
	without pointer tracing using tracePointer.
	"""

	def __init__(self, memoryEditor: MemoryEditor, baseAddress, ctype):
		"""
		Args:
			memoryEditor: MemoryEditor object used to access the memory location.
			baseAddress: The address of the memory location.
			ctype: The ctypes._SimpleCData type for determining the size of the read/write OP.
		"""

		self.me = memoryEditor
		self.baseAddress = baseAddress
		self.ctype = ctype

	def read(self):
		"""
		Reads the data stored at the memory location represented by this object.

		Returns:
			The data read.
		Raises:
			OSError: If ReadProcessMemory API failed.
		"""

		return self.me.readData(self.baseAddress, self.ctype)

	def write(self, data):
		"""
		Writes the given data to the memory location represented by this object.

		Returns:
			Number of bytes written.
		Raises:
			ValueError: If the given data does not fit into the ctype of this object.
			OSError: If WriteProcessMemory API failed.
		"""

		return self.me.writeData(self.baseAddress, self.ctype, data)

class MemoryLocationIndirect:
	"""
	The MemoryLocationDirect class is used to represent a memory location to be accessed indirectly,
	with pointer tracing using tracePointer.
	"""

	def __init__(self, memoryEditor: MemoryEditor, baseAddress, offsets, ctype):
		"""
		Args:
			memoryEditor: MemoryEditor object used to access the memory location.
			baseAddress: Initial base address to start the tracing with.
			offsets: A non-empty list containing the offsets to add to the pointer at each recursion level.
			ctype: The ctypes._SimpleCData type for determining the size of the read/write OP.
		"""

		self.me = memoryEditor
		self.baseAddress = baseAddress
		self.offsets = offsets
		self.ctype = ctype

	def read(self):
		"""
		Reads the data stored at the memory location represented by this object.

		Returns:
			The data read.
		Raises:
			OSError: If ReadProcessMemory API failed.
		"""

		pointer = self.me.tracePointer(self.baseAddress, self.offsets)
		return self.me.readData(pointer, self.ctype)

	def write(self, data):
		"""
		Writes the given data to the memory location represented by this object.

		Returns:
			Number of bytes written.
		Raises:
			ValueError: If the given data does not fit into the ctype of this object.
			OSError: If ReadProcessMemory or WriteProcessMemory API failed.
		"""

		pointer = self.me.tracePointer(self.baseAddress, self.offsets)
		return self.me.writeData(pointer, self.ctype, data)

def MemoryLocation(memoryEditor: MemoryEditor, ctype, baseAddress, offsets=None):
	"""
	Factory method that creates MemoryLocationDirect or MemoryLocationIndirect depending on whether
	offsets is None.

	Args:
		memoryEditor: MemoryEditor object used to access the memory location.
		ctype: The ctypes._SimpleCData type for determining the size of the read/write OP.
		offsets: If None, MemoryLocationDirect will be created. Otherwise, MemoryLocationIndirect will be created.
	"""

	if offsets is None:
		return MemoryLocationDirect(memoryEditor, baseAddress, ctype)
	else:
		return MemoryLocationIndirect(memoryEditor, baseAddress, offsets, ctype)
