import unittest

import fff

# https://factorio.com/blog/post/fff-247


class TestFFF(unittest.TestCase):
    maxDiff = None

    def test_image_link(self):
        html = r"""
    <h3>New office <font size="2">(kovarex)</font></h3>
    <p>
    The moving to the new office went better than expected, and with the new carpet, it feels cozy.
    </p>
    <p style="text-align: center; margin:auto; margin-top:20px; margin-bottom:20px;">
    <a href="https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-albert.jpg">
    <img style="vertical-align: top;width: 900px" src="https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-albert.jpg">
    </a>
    </p>
    
    <p style="text-align: center; margin:auto; margin-top:20px; margin-bottom:20px;">
    <a href="https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-2.jpg">
    <img style="vertical-align: top;width: 900px" src="https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-2.jpg">
    </a>
    </p>
    
    <p style="text-align: center; margin:auto; margin-top:20px; margin-bottom:20px;">
    <a href="https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-3.jpg">
    <img style="vertical-align: top;width: 900px" src="https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-3.jpg">
    </a>
    </p>
    
    <p style="text-align: center; margin:auto; margin-top:20px; margin-bottom:20px;">
    <a href="https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-4.jpg">
    <img style="vertical-align: top;width: 900px" src="https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-4.jpg">
    </a>
    </p>
    
    <p>
    We are currently using approximately 40% of the available space, so there is a room for growth if needed.
    <p>
        """

        markdown = fff.to_markdown(html)

        expected = r"""### New office (kovarex)

The moving to the new office went better than expected, and with the new carpet, it feels cozy.

[ (https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-albert.jpg) ](https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-albert.jpg)

[ (https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-2.jpg) ](https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-2.jpg)

[ (https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-3.jpg) ](https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-3.jpg)

[ (https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-4.jpg) ](https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-4.jpg)

We are currently using approximately 40% of the available space, so there is a room for growth if needed."""

        self.assertEqual(expected, markdown)

    def test_pre(self):
        html = r"""
        <pre>
        
        some <
        >
        
        code
        </pre>
        """

        markdown = fff.to_markdown(html)
        expected = r"""some <
            >
            
            code"""

        self.assertEqual(expected, markdown)

    def test_code(self):
        html = r"""<code>Hello, world!</code>"""

        markdown = fff.to_markdown(html)
        expected = r"""`Hello, world!`"""

        self.assertEqual(expected, markdown)

    def test_nested_list(self):
        html = r"""<ul>
        <li>Top Item 1</li>
        <li>Top Item 2
            <ul>
            <li>Nested Item 1</li>
            <li>Nested Item 2</li>
        </ul></li>
        <li>Top Item 3</li></ul>"""

        markdown = fff.to_markdown(html)
        expected = r"""* Top Item 1
  * Top Item 2 
    * Nested Item 1
    * Nested Item 2
  * Top Item 3"""

        self.assertEqual(expected, markdown)


if __name__ == '__main__':
    unittest.main()
