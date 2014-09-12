from io import StringIO
from .engine import SedgeEngine, ConfigOutput
from .keylib import KeyLibrary
from nose.tools import eq_


def check_parse_result(in_text, expected_text):
    library = KeyLibrary('/tmp', verbose=False)
    config = SedgeEngine(library, StringIO(in_text))
    fd = StringIO()
    out = ConfigOutput(fd)
    config.output(out)
    eq_(expected_text, fd.getvalue())


def test_empty_file():
    check_parse_result('', '')


def test_global_option():
    check_parse_result('GlobalOption\n', 'GlobalOption\n')


def test_single_host_stanza():
    check_parse_result('Host blah\n', 'Host = blah\n')


def test_expansion():
    check_parse_result('''
@with i 1 2
Host percival<i>
''', 'Host = percival1\n\nHost = percival2\n')


def test_combinatoric_expansion():
    check_parse_result('''
@with i 1 2
@with j 4 5
Host p<i>-<j>
''', 'Host = p1-4\n\nHost = p1-5\n\nHost = p2-4\n\nHost = p2-5\n')


def test_simple_is():
    check_parse_result('''
@HostAttrs a
    SomeOption Yes
Host blah
    @is a
''', 'Host = blah\n    SomeOption = Yes\n')


def test_double_is():
    check_parse_result('''
@HostAttrs a
    SomeOption Yes
@HostAttrs b
    AnotherOption No
Host blah
    @is a
    @is b
''', 'Host = blah\n    SomeOption = Yes\n    AnotherOption = No\n')


def test_via():
    check_parse_result('''
Host blah
    @via gateway
''', 'Host = blah\n    ProxyCommand = ssh gateway nc %h %p 2> /dev/null\n')


def test_include():
    check_parse_result('''
@include https://raw.githubusercontent.com/grahame/sedge/master/ci_data/simple.sedge
''', 'Host = percival\n    HostName = beaking\n    ForwardAgent = yes\n    ForwardX11 = yes\n')


def test_include_strips_root():
    check_parse_result('''
@include https://raw.githubusercontent.com/grahame/sedge/master/ci_data/strip_global.sedge
''', 'Host = percival\n    HostName = beaking\n    ForwardAgent = yes\n    ForwardX11 = yes\n')


def check_fingerprint(data, fingerprint):
    determined = KeyLibrary._fingerprint_from_keyinfo(data)
    eq_(determined, fingerprint)


def test_fingerprint_parser():
    check_fingerprint(
        '2048 aa:cb:d2:e2:00:6f:21:b4:fe:39:92:ed:eb:5e:4d:38 grahame@anglachel (RSA)',
        'aa:cb:d2:e2:00:6f:21:b4:fe:39:92:ed:eb:5e:4d:38')


def test_fingerprint_parser_double_space():
    check_fingerprint(
        '2048 aa:cb:d2:e2:00:6f:21:b4:fe:39:92:ed:eb:5e:4d:38  grahame@anglachel (RSA)',
        'aa:cb:d2:e2:00:6f:21:b4:fe:39:92:ed:eb:5e:4d:38')


def check_config_parser(s, expected):
    result = SedgeEngine.parse_config_line(s)
    eq_(result, expected)


def test_parser_noarg():
    check_config_parser('Keyword', ('Keyword', []))


def test_parser_noarg_trailingspc():
    check_config_parser('Keyword ', ('Keyword', []))


def test_parser_noarg_leadingspc():
    check_config_parser(' Keyword', ('Keyword', []))


def test_parser_onearg():
    check_config_parser('Keyword Arg1', ('Keyword', ['Arg1']))


def test_parser_onearg_dblspc():
    check_config_parser('Keyword  Arg1', ('Keyword', ['Arg1']))


def test_parser_twoargs():
    check_config_parser('Keyword Arg1 Arg2', ('Keyword', ['Arg1', 'Arg2']))


def test_parser_twoargs_dblspc():
    check_config_parser('Keyword  Arg1  Arg2', ('Keyword', ['Arg1', 'Arg2']))


def test_parser_quotearg_nospc():
    check_config_parser('Keyword "Arg1"', ('Keyword', ['Arg1']))


def test_parser_quotearg_withspc():
    check_config_parser('Keyword "Arg1 NotArg2"', ('Keyword', ['Arg1 NotArg2']))


def test_parser_quotearg_withspc_and_leading():
    check_config_parser('Keyword  "Arg1 NotArg2"', ('Keyword', ['Arg1 NotArg2']))


def test_parser_quotearg_withspc_and_trailing():
    check_config_parser('Keyword "Arg1 NotArg2" ', ('Keyword', ['Arg1 NotArg2']))


def test_parser_quotearg_withspc_and_leadin_and_trailing():
    check_config_parser('Keyword  "Arg1 NotArg2" ', ('Keyword', ['Arg1 NotArg2']))


def test_parser_quotearg_noquotearg():
    check_config_parser('Keyword "Arg1 NotArg2" Arg2', ('Keyword', ['Arg1 NotArg2', 'Arg2']))


def test_parser_noquotearg_quotearg():
    check_config_parser('Keyword Arg1 "Arg2 NotArg3"', ('Keyword', ['Arg1', 'Arg2 NotArg3']))


def test_parser_quotearg_noquotearg_quotearg():
    check_config_parser('Keyword "Arg1 NotArg2" Arg2', ('Keyword', ['Arg1 NotArg2', 'Arg2']))


def test_parser_equals_nospc():
    check_config_parser('Keyword=Value', ('Keyword', ['Value']))


def test_parser_equals_leftspc():
    check_config_parser('Keyword =Value', ('Keyword', ['Value']))


def test_parser_equals_rightspc():
    check_config_parser('Keyword= Value', ('Keyword', ['Value']))


def test_parser_equals_bothspc():
    check_config_parser('Keyword = Value', ('Keyword', ['Value']))


def test_parser_equals_allthespc():
    check_config_parser('Keyword   =   Value', ('Keyword', ['Value']))
