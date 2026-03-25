/*
 * FNV-1a 64-bit hash — thin C helper for the byte loop.
 * Called from mypyc-compiled _core.py via direct import.
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

#define FNV_OFFSET INT64_C(-3750763034362895579)
#define FNV_PRIME  INT64_C(1099511628211)

static PyObject *
py_fnv64(PyObject *module, PyObject *arg)
{
    Py_buffer buf;

    if (PyObject_GetBuffer(arg, &buf, PyBUF_SIMPLE) < 0)
        return NULL;

    const uint8_t *p = (const uint8_t *)buf.buf;
    Py_ssize_t len = buf.len;
    int64_t h = FNV_OFFSET;

    for (Py_ssize_t i = 0; i < len; i++)
        h = (h ^ p[i]) * FNV_PRIME;

    PyBuffer_Release(&buf);
    return PyLong_FromLongLong(h);
}

static PyMethodDef methods[] = {
    {"fnv64", py_fnv64, METH_O,
     "FNV-1a 64-bit hash of a bytes-like object."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_fnv64",
    NULL,
    -1,
    methods
};

PyMODINIT_FUNC
PyInit__fnv64(void)
{
    return PyModule_Create(&moduledef);
}
