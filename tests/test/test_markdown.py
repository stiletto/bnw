from twisted.trial import unittest

from bnw_web.linkify import linkify as l


class MarkdownTest(unittest.TestCase):

    def test_escaping(self):
        self.assertEqual(
            l('Test <html><body><&"\'></body></html>'),
            'Test &lt;html&gt;&lt;body&gt;&lt;&amp;&quot;&#39;&gt;&lt;/body&gt;&lt;/html&gt;')

    def test_custom_paragraphs(self):
        self.assertEqual(
            l('test\n\ntest'),
            'test\ntest')

    def test_trailing_newlines(self):
        self.assertEqual(
            l('Hi\nHi\nBye\n\n\n'),
            'Hi\nHi\nBye')

    def test_forbidden_header(self):
        self.assertEqual(
            l('abc\n#forbidden\ntest'),
            'abc\n#forbidden\ntest')

    def test_allowed_header(self):
        self.assertEqual(
            l('abc\n####allowed\ntest'),
            'abc\n<h4>allowed</h4>test')

    def test_escaping_in_header(self):
        self.assertEqual(
            l('#<bad>&amp'),
            '#&lt;bad&gt;&amp;amp')
        self.assertEqual(
            l('####<bad>&amp'),
            '<h4>&lt;bad&gt;&amp;amp</h4>')

    def test_autolink(self):
        self.assertEqual(
            l('Nyak: http://example.com/ ne nyak'),
            'Nyak: <a href="http://example.com/">http://example.com/</a> ne nyak')

    def test_forbidden_image(self):
        self.assertEqual(
            l('Look at this: ![Cool image](http://example.com/goatse.jpg)'),
            'Look at this: <a href="http://example.com/goatse.jpg">http://example.com/goatse.jpg</a>')

    def test_escaping_in_links(self):
        self.assertEqual(
            l('Bad: <http://nyan.ru/&&&>'),
            'Bad: <a href="http://nyan.ru/&amp;&amp;&amp;">http://nyan.ru/&amp;&amp;&amp;</a>')
        self.assertEqual(
            l('Look at this: ![Cool image](http://example.com/<bad>&amp;)'),
            'Look at this: <a href="http://example.com/&lt;bad&gt;&amp;amp;">http://example.com/&lt;bad&gt;&amp;amp;</a>')

    def test_inline_code(self):
        self.assertEqual(
            l('`simple code`'),
            '<code>simple code</code>')

    def test_block_code(self):
        self.assertEqual(
            l('```\ncode block\nline2\n```'),
            '<pre><code>code block\nline2</code></pre>')
        self.assertEqual(
            l('```javascript\na = 1\nb = a + 1\n```'),
            '<pre><code class="language-javascript">a = 1\nb = a + 1</code></pre>')

    def test_escaping_in_code(self):
        self.assertEqual(
            l('some\ncode: `simple <&bad code>` <- code'),
            'some\ncode: <code>simple &lt;&amp;bad code&gt;</code> &lt;- code')
        self.assertEqual(
            l('code:\n\n```\n<bad code &&&>&">\n```'),
            'code:\n<pre><code>&lt;bad code &amp;&amp;&amp;&gt;&amp;&quot;&gt;</code></pre>')
        self.assertEqual(
            l('```<bad&language>\n<bad code>\n```'),
            '<pre><code class="language-&lt;bad&amp;language&gt;">&lt;bad code&gt;</code></pre>')
