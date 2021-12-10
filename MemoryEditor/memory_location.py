from .memory_editor import MemoryEditor

class MemoryLocationDirect:
	"""
	The MemoryLocationDirect class is used to represent a memory location to be accessed directly,
	without pointer tracing using trace_pointer.
	"""

	def __init__(self, memory_editor: MemoryEditor, base_addr, ctype):
		"""
		Args:
			memory_editor: MemoryEditor object used to access the memory location.
			base_addr: The address of the memory location.
			ctype: The ctypes._SimpleCData type for determining the size of the read/write OP.
		"""

		self.me = memory_editor
		self.base_addr = base_addr
		self.ctype = ctype

	def read(self):
		"""
		Reads the data stored at the memory location represented by this object.

		Returns:
			The data read.
		Raises:
			OSError: If ReadProcessMemory API failed.
		"""

		return self.me.read_data(self.base_addr, self.ctype)

	def write(self, data):
		"""
		Writes the given data to the memory location represented by this object.

		Returns:
			Number of bytes written.
		Raises:
			ValueError: If the given data does not fit into the ctype of this object.
			OSError: If WriteProcessMemory API failed.
		"""

		return self.me.write_data(self.base_addr, self.ctype, data)

class MemoryLocationIndirect:
	"""
	The MemoryLocationDirect class is used to represent a memory location to be accessed indirectly,
	with pointer tracing using trace_pointer.
	"""

	def __init__(self, memory_editor: MemoryEditor, base_addr, offsets, ctype):
		"""
		Args:
			memory_editor: MemoryEditor object used to access the memory location.
			base_addr: Initial base address to start the tracing with.
			offsets: A non-empty list containing the offsets to add to the pointer at each recursion level.
			ctype: The ctypes._SimpleCData type for determining the size of the read/write OP.
		"""

		self.me = memory_editor
		self.base_addr = base_addr
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

		pointer = self.me.trace_pointer(self.base_addr, self.offsets)
		return self.me.read_data(pointer, self.ctype)

	def write(self, data):
		"""
		Writes the given data to the memory location represented by this object.

		Returns:
			Number of bytes written.
		Raises:
			ValueError: If the given data does not fit into the ctype of this object.
			OSError: If ReadProcessMemory or WriteProcessMemory API failed.
		"""

		pointer = self.me.trace_pointer(self.base_addr, self.offsets)
		return self.me.write_data(pointer, self.ctype, data)

def MemoryLocation(memory_editor: MemoryEditor, ctype, base_addr, offsets=None):
	"""
	Factory method that creates MemoryLocationDirect or MemoryLocationIndirect depending on whether
	offsets is None.

	Args:
		memory_editor: MemoryEditor object used to access the memory location.
		ctype: The ctypes._SimpleCData type for determining the size of the read/write OP.
		offsets: If None, MemoryLocationDirect will be created. Otherwise, MemoryLocationIndirect will be created.
	"""

	if offsets is None:
		return MemoryLocationDirect(memory_editor, base_addr, ctype)
	else:
		return MemoryLocationIndirect(memory_editor, base_addr, offsets, ctype)
