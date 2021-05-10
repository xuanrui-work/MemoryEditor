from ctypes import *
from ctypes.wintypes import *

class MemoryEditor:
	"""
	The MemoryEditor class is used to interface with Windows API inside kernel32.
	It provides interface to OpenProcess, ReadProcessMemory, WriteProcessMemory, CloseHandle.
	"""

	kernel32 = WinDLL('kernel32', use_last_error=True)

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

	@classmethod
	def openProcess(cls, dwProcessId):
		"""
		Opens an existing process for memory reading/writing access. Wrapper for OpenProcess.
		OpenProcess: https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess
		
		Args:
			dwProcessId: Process ID of the process to be opened.
		Returns:
			Open handle to the specified process. The type is HANDLE().
		Raises:
			WinError: OpenProcess API failed.
		"""

		hProcess = cls.OpenProcess(0x08 | 0x10 | 0x20, False, dwProcessId)

		if hProcess is None:
			raise WinError(get_last_error())
		return hProcess

	@classmethod
	def readProcessMemoryInBytes(cls, hProcess, lpBaseAddress, nSize):
		"""
		Copies the data in the specified address range from the address space of the specified
		process to a bytes object. Wrapper for ReadProcessMemory.
		ReadProcessMemory: https://docs.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-readprocessmemory

		Args:
			hProcess: Handle to the process with memory that is being read.
			lpBaseAddress: Pointer to the base address in the specified process from which to read.
			nSize: The number of bytes to be read from the specified address.
		Returns:
			bytearray object containing the bytes read from the address space of the specified process. The type is bytearray().
		Raises:
			WinError: ReadProcessMemory API failed.
		"""

		byteArray = bytearray(nSize)

		buffer = (c_ubyte * len(byteArray)).from_buffer(byteArray)
		bytesRead = c_size_t()

		result = cls.ReadProcessMemory(hProcess, lpBaseAddress, byref(buffer), sizeof(buffer), byref(bytesRead))

		if result == 0:
			raise WinError(get_last_error())
		return byteArray[0:bytesRead.value]

	@classmethod
	def writeProcessMemoryInBytes(cls, hProcess, lpBaseAddress, byteArray):
		"""
		Writes data from a bytearray to an area of memory in the specified process. Wrapper for WriteProcessMemory.
		WriteProcessMemory: https://docs.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-writeprocessmemory

		Args:
			hProcess: Handle to the process with memory to be modified.
			lpBaseAddress: Pointer to the base address in the specified process from which to read.
			byteArray: bytearray object containing the bytes to be written in the address space of the specified process.
		Returns:
			Number of bytes transferred into the specified process.
		Raises:
			WinError: WriteProcessMemory API failed.
		"""

		buffer = (c_ubyte * len(byteArray)).from_buffer(byteArray)
		bytesWritten = c_size_t()

		result = cls.WriteProcessMemory(hProcess, lpBaseAddress, byref(buffer), sizeof(buffer), byref(bytesWritten))

		if result == 0:
			raise WinError(get_last_error())
		return bytesWritten.value

	@classmethod
	def closeHandle(cls, hProcess):
		"""
		Closes an open handle to a process. Wrapper for CloseHandle.
		CloseHandle: https://docs.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-closehandle

		Args:
			hProcess: Handle to the process opened with openProcess
		Raises:
			WinError: CloseHandle API failed.
		"""

		result = cls.CloseHandle(hProcess)
		if result == 0:
			raise WinError(get_last_error())
