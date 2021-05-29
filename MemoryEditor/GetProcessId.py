from ctypes import *
from ctypes.wintypes import *

kernel32 = WinDLL('kernel32', use_last_error=True)

TH32CS_SNAPPROCESS = 0x0002

CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
CreateToolhelp32Snapshot.argtypes = [DWORD, DWORD]
CreateToolhelp32Snapshot.restype  = HANDLE

class PROCESSENTRY32(Structure):
	_fields_ = [
		('dwSize', DWORD),
		('cntUsage', DWORD),
		('th32ProcessID', DWORD),
		('th32DefaultHeapID', POINTER(ULONG)),
		('th32ModuleID', DWORD),
		('cntThreads', DWORD),
		('th32ParentProcessID', DWORD),
		('pcPriClassBase', LONG),
		('dwFlags', DWORD),
		('szExeFile', CHAR * 260),
	]

Process32First = kernel32.Process32First
Process32First.argtypes = [HANDLE, POINTER(PROCESSENTRY32)]
Process32First.restype  = BOOL

Process32Next = kernel32.Process32Next
Process32Next.argtypes = [HANDLE, POINTER(PROCESSENTRY32)]
Process32Next.restype  = BOOL

CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = [HANDLE]
CloseHandle.restype  = BOOL

def getProcessId(processName):
	"""
	Gets the process ID of the first process with a matching process name.

	Args:
		processName: Process name of the process to perform the process lookup.
	Raises:
		OSError: If CreateToolhelp32Snapshot, Process32First, or Process32Next API failed.
		FileNotFoundError: If the specified process name cannot be found in the system.
	"""

	hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
	if c_int64(hSnapshot).value == -1:
		raise WinError(get_last_error())

	pe32 = PROCESSENTRY32(dwSize=sizeof(PROCESSENTRY32))
	processId = None

	try:
		if not Process32First(hSnapshot, byref(pe32)):
			raise WinError(get_last_error())

		while True:
			if pe32.szExeFile.decode() == processName:
				processId = pe32.th32ProcessID
				break
			if not Process32Next(hSnapshot, byref(pe32)):
				break
		if processId is None:
			raise WinError(get_last_error())

	except OSError as osError:
		CloseHandle(hSnapshot)
		raise osError

	CloseHandle(hSnapshot)
	return processId
