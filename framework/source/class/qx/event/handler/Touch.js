/* ************************************************************************

   qooxdoo - the new era of web development

   http://qooxdoo.org

   Copyright:
     2004-2012 1&1 Internet AG, Germany, http://www.1und1.de

   License:
     LGPL: http://www.gnu.org/licenses/lgpl.html
     EPL: http://www.eclipse.org/org/documents/epl-v10.php
     See the LICENSE file in the project's top-level directory for details.

   Authors:
     * Martin Wittemann (martinwittemann)
     * Tino Butz (tbtz)
     * Christian Hagendorn (chris_schmidt)

************************************************************************ */

/**
 * This class provides a unified touch event handler.
 *
 * @require(qx.event.handler.UserAction)
 * @require(qx.event.handler.Orientation)
 * @require(qx.event.type.Tap)
 * @require(qx.event.type.Swipe)
 * @require(qx.event.type.Track)
 * @require(qx.event.type.Rotate)
 * @require(qx.event.type.Pinch)
 */
qx.Class.define("qx.event.handler.Touch",
{
  extend : qx.event.handler.TouchCore,
  implement : qx.event.IEventHandler,

  /*
  *****************************************************************************
     CONSTRUCTOR
  *****************************************************************************
  */

  /**
   * Create a new instance
   *
   * @param manager {qx.event.Manager} Event manager for the window to use
   */
  construct : function(manager)
  {
    // Define shorthands
    this.__manager = manager;
    this.__window = manager.getWindow();
    this.__root = this.__window.document;

    qx.event.handler.TouchCore.apply(this, [this.__root]);

    // IE10 works with MSPointer Events. No touch emulation needed.
    if (!qx.core.Environment.get("event.mspointer")) {
      this._initMouseObserver();
    }
  },




  /*
  *****************************************************************************
     STATICS
  *****************************************************************************
  */

  statics :
  {
    /** @type {Integer} Priority of this handler */
    PRIORITY : qx.event.Registration.PRIORITY_NORMAL,

    /** @type {Map} Supported event types */
    SUPPORTED_TYPES :
    {
      touchstart : 1,
      touchmove : 1,
      touchend : 1,
      touchcancel : 1, // Appears when the touch is interrupted, e.g. by an alert box
      tap : 1,
      longtap : 1,
      swipe : 1
    },

    /** @type {Integer} Which target check to use */
    TARGET_CHECK : qx.event.IEventHandler.TARGET_DOMNODE + qx.event.IEventHandler.TARGET_DOCUMENT,

    /** @type {Integer} Whether the method "canHandleEvent" must be called */
    IGNORE_CAN_HANDLE : true,

    /** @type {Map} Mapping of mouse events to touch events */
    MOUSE_TO_TOUCH_MAPPING :
    {
      "mousedown" : "touchstart",
      "mousemove" : "touchmove",
      "mouseup" : "touchend"
    }
  },





  /*
  *****************************************************************************
     MEMBERS
  *****************************************************************************
  */

  members :
  {
    __onMouseEventWrapper : null,

    __manager : null,
    __window : null,
    __root : null,

    // Checks if the mouse movement is happening while simulating a touch event
    __isInTouch : false,


    /*
    ---------------------------------------------------------------------------
      EVENT HANDLER INTERFACE
    ---------------------------------------------------------------------------
    */

    // interface implementation
    canHandleEvent : function(target, type) {},

    // interface implementation
    registerEvent : function(target, type, capture) {
      // Nothing needs to be done here
    },


    // interface implementation
    unregisterEvent : function(target, type, capture) {
      // Nothing needs to be done here
    },


    /*
    ---------------------------------------------------------------------------
      HELPER
    ---------------------------------------------------------------------------
    */


    /**
     * Fire a touch event with the given parameters
     *
     * @param domEvent {Event} DOM event
     * @param type {String ? null} type of the event
     * @param target {Element ? null} event target
     * @param eventTypeClass {Class ? qx.event.type.Touch} the event type class
     */
    _fireEvent : function(domEvent, type, target, eventTypeClass)
    {
      if (!target) {
        target = this._getTarget(domEvent);
      }

      var type = type || domEvent.type;

      if (target && target.nodeType)
      {
        qx.event.Registration.fireEvent(
          target,
          type,
          eventTypeClass||qx.event.type.Touch,
          [domEvent, target, null, true, true]
        );
      }

      // Fire user action event
      qx.event.Registration.fireEvent(this.__window, "useraction", qx.event.type.Data, [type]);
    },


    /*
    ---------------------------------------------------------------------------
      OBSERVER INIT
    ---------------------------------------------------------------------------
    */


    /**
     * Initializes the native mouse event listeners.
     */
    _initMouseObserver : function() {},


    /*
    ---------------------------------------------------------------------------
      OBSERVER STOP
    ---------------------------------------------------------------------------
    */


    /**
     * Disconnects the native mouse event listeners.
     */
    _stopMouseObserver : function() {},


    /*
    ---------------------------------------------------------------------------
      NATIVE EVENT OBSERVERS
    ---------------------------------------------------------------------------
    */

    /**
     * Handler for the native touch events.
     *
     * @signature function(domEvent)
     * @param domEvent {Event} The touch event from the browser.
     */
    _onTouchEvent : qx.event.GlobalError.observeMethod(function(domEvent)
    {
      this._commonTouchEventHandler(domEvent);
    }),


    /**
     * Handler for the native mouse events.
     *
     * @signature function(domEvent)
     * @param domEvent {Event} The mouse event from the browser.
     */
    _onMouseEvent : function() {},


    /**
     * Dispose this object
     */
    dispose : function()
    {
      this.__callBase("dispose");
      this._stopMouseObserver();
      this.__manager = this.__window = this.__root = null;
    },


    /**
     * Call overriden method.
     *
     * @param method {String} Name of the overriden method.
     * @param args {Array} Arguments.
     */
    __callBase: function(method, args) {
      qx.event.handler.TouchCore.prototype[method].apply(this, args || []);
    }
  },


  /*
  *****************************************************************************
     DEFER
  *****************************************************************************
  */

  defer : function(statics) {
    qx.event.Registration.addHandler(statics);

    // Prevent scrolling on the document to avoid scrolling at all
    if (qx.core.Environment.get("event.touch")) {
      if (qx.core.Environment.get("qx.mobile.nativescroll") == false)
      {
        document.addEventListener("touchmove", function(e) {
          // allow native scrolling
          var touchAction = qx.bom.element.Style.get(e.target, "touch-action") != "none";
          var webkitOverflowScrolling = qx.bom.element.Style.get(e.target, "-webkit-overflow-scrolling") === "touch";
          if (!touchAction && !webkitOverflowScrolling) {
            e.preventDefault();
          }
        });
      }

      // get the handler to asure that the instance is created
      qx.event.Registration.getManager(document).getHandler(statics);
    }
  }
});
