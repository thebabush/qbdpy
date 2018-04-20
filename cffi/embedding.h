// Functions that we export from qbdpy
int qbdipreload_on_start(void *main);
int qbdipreload_on_premain(void *gprCtx, void *fpuCtx);
int qbdipreload_on_main(int argc, char** argv);
int qbdipreload_on_run(VMInstanceRef vm, rword start, rword stop);
int qbdipreload_on_exit(int status);
