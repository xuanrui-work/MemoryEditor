from . import GetModuleBaseAddress

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

	def __init__(self, processId):
		"""
		Initializes the MemoryEditor class given a process ID. The specified process is opened automatically,
		and the handle to it is saved to hProcess.

		Args:
			processId: Process ID of the process to perform memory editing.
		Raises:
			OSError: If OpenProcess API failed.
		"""

		self.processId = processId

		hProcess = OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE, False, processId)
		if hProcess is None:
			raise WinError(get_last_error())

		self.hProcess = hProcess

	def readData(self, baseAddress, dataType):
		"""
		Reads the data in the specified address range from the address space of the opened process.

		Args:
			baseAddress: Pointer to the base address in the specified process from which to read.
			dataType: The ctypes._SimpleCData type for determining the size of the read OP.
		Returns:
			The data read.
		Raises:
			OSError: If ReadProcessMemory API failed.
		"""

		buffer = dataType()
		bytesRead = c_size_t()

		result = ReadProcessMemory(self.hProcess, baseAddress, byref(buffer), sizeof(buffer), byref(bytesRead))
		if result == 0:
			raise WinError(get_last_error())

		return buffer.value

	def writeData(self, baseAddress, dataType, data):
		"""
		Writes the given data to the specified address range in the address space of the opened process.

		Args:
			baseAddress: Pointer to the base address in the specified process to which data is written.
			dataType: The ctypes._SimpleCData type for determining the size of the write OP.
			data: The data to write.
		Returns:
			Number of bytes written.
		Raises:
			OSError: If WriteProcessMemory API failed.
		"""	

		buffer = dataType(data)
		if buffer.value != data:
			raise ValueError('The given data does not fit into the specified dataType')

		bytesWritten = c_size_t()

		result = WriteProcessMemory(self.hProcess, baseAddress, byref(buffer), sizeof(buffer), byref(bytesWritten))
		if result == 0:
			raise WinError(get_last_error())

		return bytesWritten.value

	def readByteArray(self, baseAddress, size):
		"""
		Reads the data in the specified address range from the address space of the opened process,
		into a bytearray.

		Args:
			baseAddress: Pointer to the base address in the specified process from which to read.
			size: The number of bytes to read.
		Returns:
			bytearray object containing the bytes read.
		Raises:
			OSError: If ReadProcessMemory API failed.
		"""

		byteArray = bytearray(size)

		buffer = (c_ubyte * len(byteArray)).from_buffer(byteArray)
		bytesRead = c_size_t()

		result = ReadProcessMemory(self.hProcess, baseAddress, byref(buffer), sizeof(buffer), byref(bytesRead))
		if result == 0:
			raise WinError(get_last_error())

		return byteArray[0:bytesRead.value]

	def writeByteArray(self, baseAddress, byteArray):
		"""
		Writes data from the given bytearray to the specified address range in the address space of
		the opened process.

		Args:
			baseAddress: Pointer to the base address in the specified process to which data is written.
			byteArray: bytearray object containing the bytes to write.
		Returns:
			Number of bytes written.
		Raises
			OSError: If WriteProcessMemory API failed.
		"""

		buffer = (c_ubyte * len(byteArray)).from_buffer(byteArray)
		bytesWritten = c_size_t()

		result = WriteProcessMemory(self.hProcess, baseAddress, byref(buffer), sizeof(buffer), byref(bytesWritten))
		if result == 0:
			raise WinError(get_last_error())

		return bytesWritten.value

	def close(self):
		"""
		Closes the resources opened by this MemoryEditor class.

		Raises:
			OSError: If CloseHandle API failed.
		"""

		result = CloseHandle(self.hProcess)
		if result == 0:
			raise WinError(get_last_error())

	def tracePointer(self, baseAddress, offsets):
		"""
		Traces the pointer with value baseAddress recursively to len(offsets)-1 levels, to obtain the final pointer.

		Args:
			baseAddress: Initial base address to start the tracing with.
			offsets: A non-empty list containing the offsets to add to the pointer at each recursion level.
		Returns:
			The final pointer value.
		Raises:
			IndexError: If the given offsets list is empty.
			OSError: If ReadProcessMemory API failed at any level.

		Examples:
			To evaluate [[[[baseAddress + 0x10]] + 0x30] + 0x40] + 0x50, use the following offsets:
			[0x10, 0x00, 0x30, 0x40, 0x50].
		"""

		if not offsets:
			raise IndexError('The given offsets list cannot be empty')

		p = baseAddress
		for offset in offsets[0:-1]:
			p = self.readData(p + offset, c_uint64)

		return p + offsets[-1]

	def getModuleBaseAddress(self, moduleName):
		"""
		Gets the base address of the module within the address space of the opened process.

		Args:
			moduleName: The module name of the module to lookup.
		Returns:
			The base address of the specified module.
		Raises:
			OSError: If CreateToolhelp32Snapshot, Module32First, or Module32Next API failed.
			FileNotFoundError: If the specified module cannot be found in the process.
		"""

		modBaseAddr = GetModuleBaseAddress.getModuleBaseAddress(self.processId, moduleName)
		return modBaseAddr
