/* ************************************************************************

   qooxdoo - the new era of web development

   http://qooxdoo.org

   Copyright:
     2004-2006 by 1&1 Internet AG, Germany, http://www.1and1.org

   License:
     LGPL 2.1: http://www.gnu.org/licenses/lgpl.html

   Authors:
     * Sebastian Werner (wpbasti)
     * Andreas Ecker (ecker)

************************************************************************ */

/* ************************************************************************

#module(ui_form)

************************************************************************ */

qx.OO.defineClass("qx.ui.form.Button", qx.ui.basic.Atom,
function(vText, vIcon, vIconWidth, vIconHeight, vFlash)
{
  // ************************************************************************
  //   INIT
  // ************************************************************************
  qx.ui.basic.Atom.call(this, vText, vIcon, vIconWidth, vIconHeight, vFlash);

  // Make focusable
  this.setTabIndex(1);


  // ************************************************************************
  //   MOUSE EVENTS
  // ************************************************************************
  this.addEventListener(qx.constant.Event.MOUSEOVER, this._onmouseover);
  this.addEventListener(qx.constant.Event.MOUSEOUT, this._onmouseout);
  this.addEventListener(qx.constant.Event.MOUSEDOWN, this._onmousedown);
  this.addEventListener(qx.constant.Event.MOUSEUP, this._onmouseup);


  // ************************************************************************
  //   KEY EVENTS
  // ************************************************************************
  this.addEventListener(qx.constant.Event.KEYDOWN, this._onkeydown);
  this.addEventListener(qx.constant.Event.KEYUP, this._onkeyup);
});

qx.OO.changeProperty({ name : "appearance", type : qx.constant.Type.STRING, defaultValue : "button" });

qx.Class.STATE_CHECKED = "checked";
qx.Class.STATE_PRESSED = "pressed";
qx.Class.STATE_ABANDONED = "abandoned";




/*
---------------------------------------------------------------------------
  EVENT HANDLER
---------------------------------------------------------------------------
*/

qx.Proto._onmouseover = function(e)
{
  if (e.getTarget() != this) {
    return;
  }

  if (this.hasState(qx.ui.form.Button.STATE_ABANDONED))
  {
    this.removeState(qx.ui.form.Button.STATE_ABANDONED);
    this.addState(qx.ui.form.Button.STATE_PRESSED);
  }

  this.addState(qx.ui.core.Widget.STATE_OVER);
}

qx.Proto._onmouseout = function(e)
{
  if (e.getTarget() != this) {
    return;
  }

  this.removeState(qx.ui.core.Widget.STATE_OVER);

  if (this.hasState(qx.ui.form.Button.STATE_PRESSED))
  {
    // Activate capturing if the button get a mouseout while
    // the button is pressed.
    this.setCapture(true);

    this.removeState(qx.ui.form.Button.STATE_PRESSED);
    this.addState(qx.ui.form.Button.STATE_ABANDONED);
  }
}

qx.Proto._onmousedown = function(e)
{
  if (e.getTarget() != this || !e.isLeftButtonPressed()) {
    return;
  }

  this.removeState(qx.ui.form.Button.STATE_ABANDONED);
  this.addState(qx.ui.form.Button.STATE_PRESSED);
}

qx.Proto._onmouseup = function(e)
{
  this.setCapture(false);

  // We must remove the states before executing the command 
  // because in cases were the window lost the focus while
  // executing we get the capture phase back (mouseout).
  var hasPressed = this.hasState(qx.ui.form.Button.STATE_PRESSED);
  var hasAbandoned = this.hasState(qx.ui.form.Button.STATE_ABANDONED);
  
  if (hasPressed) {
    this.removeState(qx.ui.form.Button.STATE_PRESSED);
  }
  
  if (hasAbandoned) {
    this.removeState(qx.ui.form.Button.STATE_ABANDONED);
  }

  if (!hasAbandoned)
  {
    this.addState(qx.ui.core.Widget.STATE_OVER);

    if (hasPressed) {
      this.execute();
    }
  }
}

qx.Proto._onkeydown = function(e)
{
  switch(e.getKeyCode())
  {
    case qx.event.type.KeyEvent.keys.enter:
    case qx.event.type.KeyEvent.keys.space:
      this.removeState(qx.ui.form.Button.STATE_ABANDONED);
      this.addState(qx.ui.form.Button.STATE_PRESSED);
  }
}

qx.Proto._onkeyup = function(e)
{
  switch(e.getKeyCode())
  {
    case qx.event.type.KeyEvent.keys.enter:
    case qx.event.type.KeyEvent.keys.space:
      if (this.hasState(qx.ui.form.Button.STATE_PRESSED))
      {
        this.removeState(qx.ui.form.Button.STATE_ABANDONED);
        this.removeState(qx.ui.form.Button.STATE_PRESSED);
        this.execute();
      }
  }
}








/*
---------------------------------------------------------------------------
  DISPOSER
---------------------------------------------------------------------------
*/

qx.Proto.dispose = function()
{
  if (this.getDisposed()) {
    return;
  }

  // ************************************************************************
  //   MOUSE EVENTS
  // ************************************************************************
  this.removeEventListener(qx.constant.Event.MOUSEOVER, this._onmouseover, this);
  this.removeEventListener(qx.constant.Event.MOUSEOUT, this._onmouseout, this);
  this.removeEventListener(qx.constant.Event.MOUSEDOWN, this._onmousedown, this);
  this.removeEventListener(qx.constant.Event.MOUSEUP, this._onmouseup, this);


  // ************************************************************************
  //   KEY EVENTS
  // ************************************************************************
  this.removeEventListener(qx.constant.Event.KEYDOWN, this._onkeydown, this);
  this.removeEventListener(qx.constant.Event.KEYUP, this._onkeyup, this);


  // ************************************************************************
  //   SUPER CLASS
  // ************************************************************************
  return qx.ui.basic.Atom.prototype.dispose.call(this);
}
