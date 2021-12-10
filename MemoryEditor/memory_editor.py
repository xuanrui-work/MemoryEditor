from .get_module_base_addr import get_module_base_addr

from ctypes import *
from ctypes.wintypes import *

kernel32 = WinDLL('kernel32', use_last_error=True)

PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ		 = 0x0010
PROCESS_VM_WRITE	 = 0x0020

OpenProcess = kernel32.OpenProcess
OpenProcess.argtypes = [DWORD, BOOL, DWORD]
OpenProcess.restype  = HANDLE

ReadProcessMemory = kernel32.ReadProcessMemory
ReadProcessMemory.argtypes = [HANDLE, LPCVOID, LPVOID, c_size_t, POINTER(c_size_t)]
ReadProcessMemory.restype  = BOOL

WriteProcessMemory = kernel32.WriteProcessMemory
WriteProcessMemory.argtypes = [HANDLE, LPVOID, LPCVOID, c_size_t, POINTER(c_size_t)]
WriteProcessMemory.restype  = BOOL

CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = [HANDLE]
CloseHandle.restype  = BOOL

class MemoryEditor:
	"""
	The MemoryEditor class is used to access data from the address space of the specified process,
	by utilizing native Windows APIs from kernel32.
	"""

	def __init__(self, process_id):
		"""
		Initializes the MemoryEditor class given a process ID. The specified process is opened automatically,
		and the handle to it is saved to hProcess.

		Args:
			process_id: Process ID of the process to perform memory editing.
		Raises:
			OSError: If OpenProcess API failed.
		"""

		self.process_id = process_id

		hProcess = OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE, False, process_id)
		if hProcess is None:
			raise WinError(get_last_error())

		self.hProcess = hProcess

	def read_data(self, base_addr, data_type):
		"""
		Reads the data in the specified address range from the address space of the opened process.

		Args:
			base_addr: Pointer to the base address in the specified process from which to read.
			data_type: The ctypes._SimpleCData type for determining the size of the read OP.
		Returns:
			The data read.
		Raises:
			OSError: If ReadProcessMemory API failed.
		"""

		buffer = data_type()
		bytes_read = c_size_t()

		result = ReadProcessMemory(self.hProcess, base_addr, byref(buffer), sizeof(buffer), byref(bytes_read))
		if result == 0:
			raise WinError(get_last_error())

		return buffer.value

	def write_data(self, base_addr, data_type, data):
		"""
		Writes the given data to the specified address range in the address space of the opened process.

		Args:
			base_addr: Pointer to the base address in the specified process to which data is written.
			data_type: The ctypes._SimpleCData type for determining the size of the write OP.
			data: The data to write.
		Returns:
			Number of bytes written.
		Raises:
			ValueError: If the given data does not fit into the specified data_type.
			OSError: If WriteProcessMemory API failed.
		"""	

		buffer = data_type(data)
		if buffer.value != data:
			raise ValueError('The given data does not fit into the specified data_type')

		bytes_written = c_size_t()

		result = WriteProcessMemory(self.hProcess, base_addr, byref(buffer), sizeof(buffer), byref(bytes_written))
		if result == 0:
			raise WinError(get_last_error())

		return bytes_written.value

	def read_byte_array(self, base_addr, size):
		"""
		Reads the data in the specified address range from the address space of the opened process,
		into a bytearray.

		Args:
			base_addr: Pointer to the base address in the specified process from which to read.
			size: The number of bytes to read.
		Returns:
			bytearray object containing the bytes read.
		Raises:
			OSError: If ReadProcessMemory API failed.
		"""

		byte_array = bytearray(size)

		buffer = (c_ubyte * len(byte_array)).from_buffer(byte_array)
		bytes_read = c_size_t()

		result = ReadProcessMemory(self.hProcess, base_addr, byref(buffer), sizeof(buffer), byref(bytes_read))
		if result == 0:
			raise WinError(get_last_error())

		return byte_array[0:bytes_read.value]

	def write_byte_array(self, base_addr, byte_array):
		"""
		Writes data from the given bytearray to the specified address range in the address space of
		the opened process.

		Args:
			base_addr: Pointer to the base address in the specified process to which data is written.
			byte_array: bytearray object containing the bytes to write.
		Returns:
			Number of bytes written.
		Raises
			OSError: If WriteProcessMemory API failed.
		"""

		buffer = (c_ubyte * len(byte_array)).from_buffer(byte_array)
		bytes_written = c_size_t()

		result = WriteProcessMemory(self.hProcess, base_addr, byref(buffer), sizeof(buffer), byref(bytes_written))
		if result == 0:
			raise WinError(get_last_error())

		return bytes_written.value

	def close(self):
		"""
		Closes the resources opened by this MemoryEditor class.

		Raises:
			OSError: If CloseHandle API failed.
		"""

		result = CloseHandle(self.hProcess)
		if result == 0:
			raise WinError(get_last_error())

	def trace_pointer(self, base_addr, offsets):
		"""
		Traces the pointer with value base_addr recursively to len(offsets)-1 levels, to obtain the final pointer.

		Args:
			base_addr: Initial base address to start the tracing with.
			offsets: A non-empty list containing the offsets to add to the pointer at each recursion level.
		Returns:
			The final pointer value.
		Raises:
			IndexError: If the given offsets list is empty.
			OSError: If ReadProcessMemory API failed at any level.

		Examples:
			To evaluate [[[[base_addr + 0x10]] + 0x30] + 0x40] + 0x50, use the following offsets:
			[0x10, 0x00, 0x30, 0x40, 0x50].
		"""

		if not offsets:
			raise IndexError('The given offsets list cannot be empty')

		p = base_addr
		for offset in offsets[0:-1]:
			p = self.read_data(p + offset, c_uint64)

		return p + offsets[-1]

	def get_module_base_addr(self, module_name):
		"""
		Gets the base address of the module within the address space of the opened process.

		Args:
			module_name: The module name of the module to lookup.
		Returns:
			The base address of the specified module.
		Raises:
			OSError: If CreateToolhelp32Snapshot, Module32First, or Module32Next API failed.
			FileNotFoundError: If the specified module cannot be found in the process.
		"""

		module_base_addr = get_module_base_addr(self.process_id, module_name)
		return module_base_addr
