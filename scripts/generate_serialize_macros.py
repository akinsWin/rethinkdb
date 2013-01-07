#!/usr/bin/env python
# Copyright 2010-2012 RethinkDB, all rights reserved.
import sys

"""This script is used to generate the RDB_MAKE_SERIALIZABLE_*() and
RDB_MAKE_ME_SERIALIZABLE_*() macro definitions. Because there are so
many variations, and because they are so similar, it's easier to just
have a Python script to generate them.

This script is meant to be run as follows (assuming you are in the
"rethinkdb/src" directory):

$ ../scripts/generate_serialize_macros.py > rpc/serialize_macros.hpp

"""


def generate_make_serializable_macro(nfields):
    print "#define RDB_EXPAND_SERIALIZABLE_%d(function_attr, type_t%s) \\" % \
        (nfields, "".join(", field%d" % (i+1) for i in xrange(nfields)))
    zeroarg = ("UNUSED " if nfields == 0 else "")
    print "    function_attr write_message_t &operator<<(%swrite_message_t &msg /* NOLINT */, %sconst type_t &thing) { \\" % (zeroarg, zeroarg)
    for i in xrange(nfields):
        print "        msg << thing.field%d; \\" % (i + 1)
    print "    return msg; \\"
    print "    } \\"
    print "    function_attr archive_result_t deserialize(%sread_stream_t *s, %stype_t *thing) { \\" % (zeroarg, zeroarg)
    print "        archive_result_t res = ARCHIVE_SUCCESS; \\"
    for i in xrange(nfields):
        print "        res = deserialize(s, &thing->field%d); \\" % (i + 1)
        print "        if (res) { return res; } \\"
    print "        return res; \\"
    print "    } \\"
    # See the note in the comment below.
    print "    extern int dont_use_RDB_EXPAND_SERIALIZABLE_within_a_class_body"
    print "#define RDB_MAKE_SERIALIZABLE_%d(...) RDB_EXPAND_SERIALIZABLE_%d(inline, __VA_ARGS__)" % (nfields, nfields)
    print "#define RDB_IMPL_SERIALIZABLE_%d(...) RDB_EXPAND_SERIALIZABLE_%d(, __VA_ARGS__)" % (nfields, nfields)

def generate_make_me_serializable_macro(nfields):
    print "#define RDB_MAKE_ME_SERIALIZABLE_%d(%s) \\" % \
        (nfields, ", ".join("field%d" % (i+1) for i in xrange(nfields)))
    zeroarg = ("UNUSED " if nfields == 0 else "")
    print "    friend class write_message_t; \\"
    print "    void rdb_serialize(%swrite_message_t &msg /* NOLINT */) const { \\" % zeroarg
    for i in xrange(nfields):
        print "        msg << field%d; \\" % (i + 1)
    print "    } \\"
    print "    friend class archive_deserializer_t; \\"
    print "    archive_result_t rdb_deserialize(%sread_stream_t *s) { \\" % zeroarg
    print "        archive_result_t res = ARCHIVE_SUCCESS; \\"
    for i in xrange(nfields):
        print "        res = deserialize(s, &field%d); \\" % (i + 1)
        print "        if (res) { return res; } \\"
    print "        return res; \\"
    print "    }"

def generate_impl_me_serializable_macro(nfields):
    print "#define RDB_IMPL_ME_SERIALIZABLE_%d(typ%s) \\" % \
        (nfields, "".join(", field%d" % (i+1) for i in xrange(nfields)))
    zeroarg = ("UNUSED " if nfields == 0 else "")
    print "    void typ::rdb_serialize(%swrite_message_t &msg /* NOLINT */) const { \\" % zeroarg
    for i in xrange(nfields):
        print "        msg << field%d; \\" % (i + 1)
    print "    } \\"
    print "    archive_result_t typ::rdb_deserialize(%sread_stream_t *s) { \\" % zeroarg
    print "        archive_result_t res = ARCHIVE_SUCCESS; \\"
    for i in xrange(nfields):
        print "        res = deserialize(s, &field%d); \\" % (i + 1)
        print "        if (res) { return res; } \\"
    print "        return res; \\"
    print "    }"

if __name__ == "__main__":

    print "// Copyright 2010-2012 RethinkDB, all rights reserved."
    print "#ifndef RPC_SERIALIZE_MACROS_HPP_"
    print "#define RPC_SERIALIZE_MACROS_HPP_"
    print

    print "/* This file is automatically generated by '%s'." % " ".join(sys.argv)
    print "Please modify '%s' instead of modifying this file.*/" % sys.argv[0]
    print

    print "#include \"containers/archive/archive.hpp\""
    print "#include \"containers/archive/stl_types.hpp\""
    print

    print """
/* The purpose of these macros is to make it easier to serialize and
unserialize data types that consist of a simple series of fields, each of which
is serializable. Suppose we have a type "struct point_t { int x, y; }" that we
want to be able to serialize. To make it serializable automatically, either
write RDB_MAKE_SERIALIZABLE_2(point_t, x, y) at the global scope or write
RDB_MAKE_ME_SERIALIZABLE(x, y) within the body of the point_t type.
The reason for the second form is to make it possible to serialize template
types. There is at present no non-intrusive way to use these macros to
serialize template types; this is less-than-ideal, but not worth fixing right
now.

A note about "dont_use_RDB_MAKE_SERIALIZABLE_within_a_class_body": It's wrong
to invoke RDB_MAKE_SERIALIZABLE_*() within the body of a class. You should
invoke it at global scope after the class declaration, or use
RDB_MAKE_ME_SERIALIZABLE_*() instead. In order to force the compiler to catch
this error, we declare a dummy "extern int" in RDB_MAKE_ME_SERIALIZABLE_*().
This is a noop at the global scope, but produces a (somewhat weird) error in
the class scope. */
    """.strip()
    print
    print "#define RDB_DECLARE_SERIALIZABLE(type_t) \\"
    print "    write_message_t &operator<<(write_message_t &, const type_t &); \\"
    print "    archive_result_t deserialize(read_stream_t *s, type_t *thing)"
    print
    print "#define RDB_DECLARE_ME_SERIALIZABLE \\"
    print "    void rdb_serialize(write_message_t &msg /* NOLINT */) const; \\"
    print "    friend class archive_deserializer_t; \\"
    print "    archive_result_t rdb_deserialize(read_stream_t *s)"
    print

    for nfields in xrange(20):
        generate_make_serializable_macro(nfields)
        print
        generate_make_me_serializable_macro(nfields)
        print
        generate_impl_me_serializable_macro(nfields)
        print

    print "#endif // RPC_SERIALIZE_MACROS_HPP_"
