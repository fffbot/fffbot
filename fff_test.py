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

    def test_find_images(self):
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
    <img style="vertical-align: top;width: 900px" 
    src="https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-2.jpg">
    </a>
    </p>
    
    <img src="https://i.imgur.com/1xRAbt2.jpg">
    
    <p style="text-align: center; margin:auto; margin-top:20px; margin-bottom:20px;">
    <a href="https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-3.jpg">
    <img style="vertical-align: top;width: 900px"
     
     src="https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-3.jpg"
     
     >
    </a>
    </p>
    
    <p style="text-align: center; margin:auto; margin-top:20px; margin-bottom:20px;">
    <a href="https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-4.jpg">
    <img style="vertical-align: top;width: 900px" src="https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-4.jpg"/>
    </a>
    
    <img style="vertical-align: top;width: 900px" 
    src="https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-4.jpg"
    /
    >
    </p>
    
    <p>
    We are currently using approximately 40% of the available space, so there is a room for growth if needed.
    <p>
        """

        urls = fff.find_images(html)
        expected = {'https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-2.jpg',
                    'https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-3.jpg',
                    'https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-4.jpg',
                    'https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-albert.jpg'}

        self.assertEqual(expected, urls)

    def test_replace_images(self):
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
    <img style="vertical-align: top;width: 900px" 
    src="https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-2.jpg">
    </a>
    </p>
    
    <p style="text-align: center; margin:auto; margin-top:20px; margin-bottom:20px;">
    <a href="https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-3.jpg">
    <img style="vertical-align: top;width: 900px"
     
     src="https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-3.jpg"
     
     >
    </a>
    </p>
    
    <p style="text-align: center; margin:auto; margin-top:20px; margin-bottom:20px;">
    <a href="https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-4.jpg">
    <img style="vertical-align: top;width: 900px" src="https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-4.jpg"/>
    </a>
    
    <img style="vertical-align: top;width: 900px" 
    src="https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-4.jpg"
    /
    >
    </p>
    
    <p>
    We are currently using approximately 40% of the available space, so there is a room for growth if needed.
    <p>
        """

        images = {'https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-2.jpg': 'replacement1',
                    'https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-3.jpg': 'replacement2',
                    'https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-4.jpg': 'replacement3',
                    'https://eu2.factorio.com/assets/img/blog/fff-243-office-picture-albert.jpg': 'replacement4'}

        replaced = fff.replace_images(html, images)

        expected = r"""
    <h3>New office <font size="2">(kovarex)</font></h3>
    <p>
    The moving to the new office went better than expected, and with the new carpet, it feels cozy.
    </p>
    <p style="text-align: center; margin:auto; margin-top:20px; margin-bottom:20px;">
    <a href="replacement4">
    <img style="vertical-align: top;width: 900px" src="replacement4">
    </a>
    </p>
    
    <p style="text-align: center; margin:auto; margin-top:20px; margin-bottom:20px;">
    <a href="replacement1">
    <img style="vertical-align: top;width: 900px" 
    src="replacement1">
    </a>
    </p>
    
    <p style="text-align: center; margin:auto; margin-top:20px; margin-bottom:20px;">
    <a href="replacement2">
    <img style="vertical-align: top;width: 900px"
     
     src="replacement2"
     
     >
    </a>
    </p>
    
    <p style="text-align: center; margin:auto; margin-top:20px; margin-bottom:20px;">
    <a href="replacement3">
    <img style="vertical-align: top;width: 900px" src="replacement3"/>
    </a>
    
    <img style="vertical-align: top;width: 900px" 
    src="replacement3"
    /
    >
    </p>
    
    <p>
    We are currently using approximately 40% of the available space, so there is a room for growth if needed.
    <p>
        """

        self.assertEqual(expected, replaced)

    def test_extract_fff_number(self):
        self.assertEqual('259', fff.extract_fff_number('https://www.factorio.com/blog/post/fff-259'))

    def test_convert_images(self):
        result = fff.convert_web_videos_to_img("""
        <p>
                With the new high resolution Worms (and now also Spitters), their projectiles started to look even more out of place than before. On top of that, a homing acid projectile makes about as much sense as a homing laser beam. We were quite sure we want Worms and Spitters to spit acid, but closer to how the flamethrower 'stream attack' behaves, so we started with that.
            </p>

            <p style="text-align: center; margin:auto; margin-top:20px; margin-bottom: 20px;">
                <video width="896" autoplay muted loop playsinline>
                    <source src="https://cdn.factorio.com/assets/img/blog/fff-279-no-prediction.webm"
                            type='video/webm'/>
                    <source src="https://cdn.factorio.com/assets/img/blog/fff-279-no-prediction.mp4"
                            type='video/mp4'/>
                    Webm/Mp4 playback not supported on your device.
                </video>
            </p>

            <p>
                While visually it makes much better sense and the acid looks much nicer thanks to the work of Dominik (from the GFX gang, not pipe programmer gang) and Ernestas, the acid stream has a downside - it can easily be dodged. In fact, as long as you keep moving, the stream never hits you. Therefore we added predictive targeting to streams - so Worms, Spitters and Flamethrower turrets can hit the target unless it changes direction.
                It is still possible for the player to dodge them if they try, but with higher numbers of Worms it becomes a lot harder.
            </p>

            <p style="text-align: center; margin:auto; margin-top:20px; margin-bottom: 20px;">
                <video width="896" autoplay muted loop playsinline>
                    <source src="https://cdn.factorio.com/assets/img/blog/fff-279-prediction.webm"
                            type='video/webm'/>
                    <source src="https://cdn.factorio.com/assets/img/blog/fff-279-prediction.mp4"
                            type='video/mp4'/>
                    Webm/Mp4 playback not supported on your device.
                </video>
            </p>

            <p>
                When the target too fast and/or the predicted position is out of range, the prediction is turned off. We will probably tweak this so that the prediction tries to go as close to the border of its range as possible. At some point even the homing projectiles from 0.16 miss so this is not much difference, the threshold probably comes a little earlier though.
            </p>
""")
        expected = """
        <p>
                With the new high resolution Worms (and now also Spitters), their projectiles started to look even more out of place than before. On top of that, a homing acid projectile makes about as much sense as a homing laser beam. We were quite sure we want Worms and Spitters to spit acid, but closer to how the flamethrower 'stream attack' behaves, so we started with that.
            </p>

            <p style="text-align: center; margin:auto; margin-top:20px; margin-bottom: 20px;">
                <img src="https://cdn.factorio.com/assets/img/blog/fff-279-no-prediction.webm"/>
            </p>

            <p>
                While visually it makes much better sense and the acid looks much nicer thanks to the work of Dominik (from the GFX gang, not pipe programmer gang) and Ernestas, the acid stream has a downside - it can easily be dodged. In fact, as long as you keep moving, the stream never hits you. Therefore we added predictive targeting to streams - so Worms, Spitters and Flamethrower turrets can hit the target unless it changes direction.
                It is still possible for the player to dodge them if they try, but with higher numbers of Worms it becomes a lot harder.
            </p>

            <p style="text-align: center; margin:auto; margin-top:20px; margin-bottom: 20px;">
                <img src="https://cdn.factorio.com/assets/img/blog/fff-279-prediction.webm"/>
            </p>

            <p>
                When the target too fast and/or the predicted position is out of range, the prediction is turned off. We will probably tweak this so that the prediction tries to go as close to the border of its range as possible. At some point even the homing projectiles from 0.16 miss so this is not much difference, the threshold probably comes a little earlier though.
            </p>
"""
        self.assertEqual(expected, result)


    def test_youtube_embed(self):
        result = fff.convert_youtube_embed("""
        <p>
        Overall bug fixing is going well. We had a rough release earlier this week related to some GUI logic not working correctly. In the past we've talked about our automated test system (<a href="https://www.factorio.com/blog/post/fff-186">FFF-186</a>) which normally tests game logic. With the rough release earlier this week it pushed me to get the test system in a shape where we can run automatic graphics tests (in hopes of avoiding the issues we had during the 2 broken versions). We still have a few small things to fix but otherwise the automatic test system can now run the full graphics interface while running the tests (in parallel). Just for fun, I set it up so it would arrange the windows in a grid:
        </p>
        
        <p style="text-align: center; margin:auto; margin-top:20px; margin-bottom: 20px;">
        <iframe width="896" height="560" src="https://www.youtube.com/embed/LXnyTZBmfXM" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
        </p>
        
        <h3>New remnants for almost everything <font size=2>Dom, Albert</font></h3>
        <p>
        Since forever, when killing an entity we used generic remnants (with a few exceptions, walls, rails...). We only cared about the size of the entity and it is done.
        </p>

        <p>
        Just wow.
        </p>
        
        <p style="text-align: center; margin:auto; margin-top:20px; margin-bottom: 20px;">
        <iframe width="896" height="504" src="https://www.youtube.com/embed/7lVAFcDX4eM" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
        </p>
        
        <p>
        As always, let us know what you think on our <a href="https://forums.factorio.com/70004">forum</a>.
        </p>
""")
        expected = """
        <p>
        Overall bug fixing is going well. We had a rough release earlier this week related to some GUI logic not working correctly. In the past we've talked about our automated test system (<a href="https://www.factorio.com/blog/post/fff-186">FFF-186</a>) which normally tests game logic. With the rough release earlier this week it pushed me to get the test system in a shape where we can run automatic graphics tests (in hopes of avoiding the issues we had during the 2 broken versions). We still have a few small things to fix but otherwise the automatic test system can now run the full graphics interface while running the tests (in parallel). Just for fun, I set it up so it would arrange the windows in a grid:
        </p>
        
        <p style="text-align: center; margin:auto; margin-top:20px; margin-bottom: 20px;">
        <a href="https://www.youtube.com/watch?v=LXnyTZBmfXM">https://www.youtube.com/watch?v=LXnyTZBmfXM</a>
        </p>
        
        <h3>New remnants for almost everything <font size=2>Dom, Albert</font></h3>
        <p>
        Since forever, when killing an entity we used generic remnants (with a few exceptions, walls, rails...). We only cared about the size of the entity and it is done.
        </p>

        <p>
        Just wow.
        </p>
        
        <p style="text-align: center; margin:auto; margin-top:20px; margin-bottom: 20px;">
        <a href="https://www.youtube.com/watch?v=7lVAFcDX4eM">https://www.youtube.com/watch?v=7lVAFcDX4eM</a>
        </p>
        
        <p>
        As always, let us know what you think on our <a href="https://forums.factorio.com/70004">forum</a>.
        </p>
"""
        self.assertEqual(expected, result)

if __name__ == '__main__':
    unittest.main()
