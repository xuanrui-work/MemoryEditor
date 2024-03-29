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

def get_process_id(process_name):
	"""
	Gets the process ID of the first process with a matching process name.

	Args:
		process_name: Process name of the process to perform the process lookup.
	Raises:
		OSError: If CreateToolhelp32Snapshot, Process32First, or Process32Next API failed.
		FileNotFoundError: If the specified process name cannot be found in the system.
	"""

	h_snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
	if c_int64(h_snapshot).value == -1:
		raise WinError(get_last_error())

	pe32 = PROCESSENTRY32(dwSize=sizeof(PROCESSENTRY32))
	process_id = None

	try:
		if not Process32First(h_snapshot, byref(pe32)):
			raise WinError(get_last_error())

		while True:
			if pe32.szExeFile.decode() == process_name:
				process_id = pe32.th32ProcessID
				break
			if not Process32Next(h_snapshot, byref(pe32)):
				break
		if process_id is None:
			raise WinError(get_last_error())

	except OSError as os_error:
		CloseHandle(h_snapshot)
		raise os_error

	CloseHandle(h_snapshot)
	return process_id
