 // Priority+ Scrolling Menu v1.0: http://www.dynamicdrive.com

        // Add "can-touch" to document root on touch: http://www.javascriptkit.com/dhtmltutors/sticky-hover-issue-solutions.shtml

        ; (function () {
            var isTouch = false //var to indicate current input type (is touch versus no touch) 
            var isTouchTimer
            var curRootClass = '' //var indicating current document root class ("can-touch" or "")

            function addtouchclass(e) {
                clearTimeout(isTouchTimer)
                isTouch = true
                if (curRootClass != 'can-touch') { //add "can-touch' class if it's not already present
                    curRootClass = 'can-touch'
                    document.documentElement.classList.add(curRootClass)
                }
                isTouchTimer = setTimeout(function () { isTouch = false }, 1000) //maintain "istouch" state for 1000ms so removetouchclass doesn't get fired immediately following a touch event
            }

            function removetouchclass(e) {
                if (!isTouch && curRootClass == 'can-touch') { //remove 'can-touch' class if not triggered by a touch event and class is present
                    isTouch = false
                    curRootClass = ''
                    document.documentElement.classList.remove('can-touch')
                }
            }

            if (document.documentElement.classList) {
                document.addEventListener('touchstart', addtouchclass, false) //this event only gets called when input type is touch
                document.addEventListener('mouseover', removetouchclass, false) //this event gets called when input type is everything from touch to mouse/ trackpad
            }
        })();

        // Priority Scrolling main function

        ; (function () {

            var settings = {
                mouserange: '20%', // Specify range on both ends of menu where mouse triggers scrolling (in pct)
                rightOffset: 1 // Specify additional pixels to scroll after right edge of window (recommend at least 17 to account for browser scroll bar)
            }

            function getoffset(what, offsettype) { // custom get element offset from document (since jQuery version is whack in mobile browsers
                return (what.offsetParent) ? what[offsettype] + getoffset(what.offsetParent, offsettype) : what[offsettype]
            }

            function getcss3prop(cssprop) {
                var css3vendors = ['', '-moz-', '-webkit-', '-o-', '-ms-', '-khtml-']
                var root = document.documentElement
                function camelCase(str) {
                    return str.replace(/\-([a-z])/gi, function (match, p1) { // p1 references submatch in parentheses
                        return p1.toUpperCase() // convert first letter after "-" to uppercase
                    })
                }
                for (var i = 0; i < css3vendors.length; i++) {
                    var css3propcamel = camelCase(css3vendors[i] + cssprop)
                    if (css3propcamel.substr(0, 2) == 'Ms') // if property starts with 'Ms'
                        css3propcamel = 'm' + css3propcamel.substr(1) // Convert 'M' to lowercase
                    if (css3propcamel in root.style)
                        return css3propcamel
                }
                return undefined
            }

            function intializeMenu(menuid) {
                var priorityscroll = document.getElementById(menuid)
                var hamburgermenu = priorityscroll.querySelector('ul')
                var prioritywidth
                var hamburgermenuwidth
                var menuoffsetLeft
                var transformprop = getcss3prop('transform')
                var resizetimer, curscrollDir, rightmost

                function updateMeasures() {
                    menuoffsetLeft = getoffset(priorityscroll, 'offsetLeft')
                    prioritywidth = priorityscroll.offsetWidth
                    hamburgermenuwidth = hamburgermenu.scrollWidth
                    hamburgermenu.style[transformprop] = 'translateX(0)'
                }

                updateMeasures()

                hamburgermenu.addEventListener('mousemove', function (e) {
                    if (document.documentElement.classList.contains('can-touch'))
                        return
                    var rangenumber = prioritywidth * parseInt(settings.mouserange) / 100
                    var therange = [rangenumber, prioritywidth - rangenumber]
                    var relativemouseX = e.pageX - menuoffsetLeft
                    if (relativemouseX < therange[0]) {
                        hamburgermenu.style[transformprop] = 'translateX(0px)'
                        curscrollDir = 'left'
                    }
                    else if (relativemouseX > therange[1] && hamburgermenuwidth > prioritywidth) {
                        rightmost = -(hamburgermenuwidth - prioritywidth + settings.rightOffset)
                        hamburgermenu.style[transformprop] = 'translateX(' + rightmost + 'px)'
                        curscrollDir = 'right'
                    }
                }, false)

                hamburgermenu.addEventListener('mouseleave', function (e) {
                    var matrix = window.getComputedStyle(hamburgermenu).getPropertyValue(transformprop)
                    //get transform values: http://stackoverflow.com/questions/21987596/get-css-transform-property-with-jquery
                    matrix = matrix.replace(/[^0-9\-.,]/g, '').split(',')
                    var translateX = parseInt(matrix[12] || matrix[4])
                    translateX = curscrollDir == 'left' ? Math.min(translateX + 20, 0) : Math.max(translateX - 20, rightmost)
                    hamburgermenu.style[transformprop] = 'translateX(' + translateX + 'px)'
                }, false)


                window.addEventListener('resize', function () {
                    clearTimeout(resizetimer)
                    resizetimer = setTimeout(function () {
                        updateMeasures()
                    }, 300)
                }, false)

                window.addEventListener('load', function () {
                    updateMeasures()
                }, false)

            }

            document.addEventListener("DOMContentLoaded", function () {
                intializeMenu('priorityscroll')
            })

        }())