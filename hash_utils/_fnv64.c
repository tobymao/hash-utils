/*
 * FNV-1a 64-bit hash — C extension for deterministic hashing.
 *
 * Handles str (zero-copy UTF-8), bytes, bytearray via FNV-1a.
 * Falls back to Python hash() for int/float (already deterministic).
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

#define FNV_OFFSET INT64_C(-3750763034362895579)
#define FNV_PRIME  INT64_C(1099511628211)

static inline int64_t
fnv64(const uint8_t *p, Py_ssize_t len)
{
    int64_t h = FNV_OFFSET;
    for (Py_ssize_t i = 0; i < len; i++)
        h = (h ^ p[i]) * FNV_PRIME;
    return h;
}

static PyObject *
py_fnv64(PyObject *module, PyObject *arg)
{
    if (PyUnicode_Check(arg)) {
        Py_ssize_t len;
        const uint8_t *p = (const uint8_t *)PyUnicode_AsUTF8AndSize(arg, &len);
        if (!p)
            return NULL;
        return PyLong_FromLongLong(fnv64(p, len));
    }
    if (PyBytes_Check(arg)) {
        return PyLong_FromLongLong(
            fnv64((const uint8_t *)PyBytes_AS_STRING(arg),
                  PyBytes_GET_SIZE(arg)));
    }
    if (PyByteArray_Check(arg)) {
        return PyLong_FromLongLong(
            fnv64((const uint8_t *)PyByteArray_AS_STRING(arg),
                  PyByteArray_GET_SIZE(arg)));
    }
    /* int, float, tuple, etc. — hash() is deterministic for these */
    Py_hash_t h = PyObject_Hash(arg);
    if (h == -1 && PyErr_Occurred())
        return NULL;
    return PyLong_FromLongLong((int64_t)h);
}

static PyMethodDef methods[] = {
    {"fnv64", py_fnv64, METH_O,
     "Deterministic i64 hash: FNV-1a for str/bytes/bytearray, Python hash() for other types."},
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
