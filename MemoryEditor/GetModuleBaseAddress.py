from ctypes import *
from ctypes.wintypes import *

kernel32 = WinDLL('kernel32', use_last_error=True)

TH32CS_SNAPMODULE	= 0x0008
TH32CS_SNAPMODULE32 = 0x0010

CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
CreateToolhelp32Snapshot.argtypes = [DWORD, DWORD]
CreateToolhelp32Snapshot.restype  = HANDLE

class MODULEENTRY32(Structure):
	_fields_ = [
		('dwSize', DWORD),
		('th32ModuleID', DWORD),
		('th32ProcessID', DWORD),
		('GlblcntUsage', DWORD),
		('ProccntUsage', DWORD),
		('modBaseAddr', POINTER(BYTE)),
		('modBaseSize', DWORD),
		('hModule', HMODULE),
		('szModule', c_char * 256),
		('szExePath', c_char * 260),
	]

Module32First = kernel32.Module32First
Module32First.argtypes = [HANDLE, POINTER(MODULEENTRY32)]
Module32First.restype  = BOOL

Module32Next = kernel32.Module32Next
Module32Next.argtypes = [HANDLE, POINTER(MODULEENTRY32)]
Module32Next.restype  = BOOL

CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = [HANDLE]
CloseHandle.restype  = BOOL

def getModuleBaseAddress(processId, moduleName):
	"""
	Gets the base address of the module within the address space of the specified process.

	Args:
		processId: Process ID of the process to perform the module lookup.
		moduleName: The module name of the module to lookup.
	Returns:
		The base address of the specified module.
	Raises:
		OSError: If CreateToolhelp32Snapshot, Module32First, or Module32Next API failed.
		FileNotFoundError: If the specified module cannot be found in the process.
	"""

	hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, processId)
	if c_int64(hSnapshot).value == -1:
		raise WinError(get_last_error())

	me32 = MODULEENTRY32(dwSize=sizeof(MODULEENTRY32))
	modBaseAddr = None

	if not Module32First(hSnapshot, byref(me32)):
		raise WinError(get_last_error())

	while True:
		if me32.szModule.decode() == moduleName:
			modBaseAddr = me32.modBaseAddr
			break
		if not Module32Next(hSnapshot, byref(me32)):
			break

	winerror = get_last_error()
	CloseHandle(hSnapshot)

	if modBaseAddr is None:
		raise WinError(winerror)

	modBaseAddr = cast(modBaseAddr, c_void_p)
	return modBaseAddr.value
