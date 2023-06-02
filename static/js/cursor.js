/*!
 * wavesurfer.js cursor plugin 6.6.3 (2023-04-04)
 * https://wavesurfer-js.org
 * @license BSD-3-Clause
 */
! function(e, t) {
    "object" == typeof exports && "object" == typeof module ? module.exports = t() : "function" == typeof define && define.amd ? define("WaveSurfer", [], t) : "object" == typeof exports ? exports.WaveSurfer = t() : (e.WaveSurfer = e.WaveSurfer || {}, e.WaveSurfer.cursor = t())
}(self, (() => (() => {
    "use strict";
    var e = {
            178: (e, t) => {
                function i(e) {
                    return i = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function(e) {
                        return typeof e
                    } : function(e) {
                        return e && "function" == typeof Symbol && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e
                    }, i(e)
                }

                function r(e, t) {
                    for (var i = 0; i < t.length; i++) {
                        var r = t[i];
                        r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, o(r.key), r)
                    }
                }

                function s(e, t, i) {
                    return (t = o(t)) in e ? Object.defineProperty(e, t, {
                        value: i,
                        enumerable: !0,
                        configurable: !0,
                        writable: !0
                    }) : e[t] = i, e
                }

                function o(e) {
                    var t = function(e, t) {
                        if ("object" !== i(e) || null === e) return e;
                        var r = e[Symbol.toPrimitive];
                        if (void 0 !== r) {
                            var s = r.call(e, t || "default");
                            if ("object" !== i(s)) return s;
                            throw new TypeError("@@toPrimitive must return a primitive value.")
                        }
                        return ("string" === t ? String : Number)(e)
                    }(e, "string");
                    return "symbol" === i(t) ? t : String(t)
                }
                Object.defineProperty(t, "__esModule", {
                    value: !0
                }), t.default = void 0;
                var a = function() {
                    function e(t, i) {
                        var r = this;
                        ! function(e, t) {
                            if (!(e instanceof t)) throw new TypeError("Cannot call a class as a function")
                        }(this, e), s(this, "defaultParams", {
                            hideOnBlur: !0,
                            width: "1px",
                            color: "black",
                            opacity: "0.25",
                            style: "solid",
                            zIndex: 4,
                            customStyle: {},
                            customShowTimeStyle: {},
                            showTime: !1,
                            followCursorY: !1,
                            formatTimeCallback: null
                        }), s(this, "_onMousemove", (function(e) {
                            var t = r.util.withOrientation(e, r.wavesurfer.params.vertical),
                                i = r.wrapper.getBoundingClientRect(),
                                s = 0,
                                o = r.wrapper.scrollLeft + t.clientX - i.left,
                                a = r.displayTime ? r.displayTime.getBoundingClientRect().width : 0,
                                n = i.right < t.clientX + a;
                            r.params.showTime && r.params.followCursorY && (s = t.clientY - (i.top + i.height / 2)), r.updateCursorPosition(o, s, n)
                        })), s(this, "_onMouseenter", (function() {
                            return r.showCursor()
                        })), s(this, "_onMouseleave", (function() {
                            return r.hideCursor()
                        })), this.wavesurfer = i, this.style = i.util.style, this.util = i.util, this.cursor = null, this.showTime = null, this.displayTime = null, this.isDestroyCalled = !1, this.params = Object.assign({}, this.defaultParams, t)
                    }
                    var t, i, o;
                    return t = e, i = [{
                        key: "_onReady",
                        value: function() {
                            this.isDestroyCalled || (this.wrapper = this.wavesurfer.drawer.wrapper, this.cursor = this.util.withOrientation(this.wrapper.appendChild(document.createElement("cursor")), this.wavesurfer.params.vertical), this.style(this.cursor, Object.assign({
                                position: "absolute",
                                zIndex: this.params.zIndex,
                                left: 0,
                                top: 0,
                                bottom: 0,
                                width: "0",
                                display: "flex",
                                borderRightStyle: this.params.style,
                                borderRightWidth: this.params.width,
                                borderRightColor: this.params.color,
                                opacity: this.params.opacity,
                                pointerEvents: "none"
                            }, this.params.customStyle)), this.params.showTime && (this.showTime = this.util.withOrientation(this.wrapper.appendChild(document.createElement("showTitle")), this.wavesurfer.params.vertical), this.style(this.showTime, Object.assign({
                                position: "absolute",
                                zIndex: this.params.zIndex,
                                left: 0,
                                top: 0,
                                bottom: 0,
                                width: "auto",
                                display: "flex",
                                opacity: this.params.opacity,
                                pointerEvents: "none",
                                height: "100%"
                            }, this.params.customStyle)), this.displayTime = this.util.withOrientation(this.showTime.appendChild(document.createElement("div")), this.wavesurfer.params.vertical), this.style(this.displayTime, Object.assign({
                                display: "inline",
                                pointerEvents: "none",
                                margin: "auto",
                                visibility: "hidden"
                            }, this.params.customShowTimeStyle)), this.displayTime.innerHTML = this.formatTime(0)), this.wrapper.addEventListener("mousemove", this._onMousemove), this.params.hideOnBlur && (this.hideCursor(), this.wrapper.addEventListener("mouseenter", this._onMouseenter), this.wrapper.addEventListener("mouseleave", this._onMouseleave)))
                        }
                    }, {
                        key: "init",
                        value: function() {
                            var e = this;
                            this.wavesurfer.isReady ? this._onReady() : this.wavesurfer.once("ready", (function() {
                                return e._onReady()
                            }))
                        }
                    }, {
                        key: "destroy",
                        value: function() {
                            this.cursorTime && this.showTime ? (this.params.showTime && this.showTime && this.showTime.remove(), this.cursor && this.cursor.remove(), this.wrapper.removeEventListener("mousemove", this._onMousemove), this.params.hideOnBlur && (this.wrapper.removeEventListener("mouseenter", this._onMouseenter), this.wrapper.removeEventListener("mouseleave", this._onMouseleave))) : this.isDestroyCalled = !0
                        }
                    }, {
                        key: "updateCursorPosition",
                        value: function(e, t) {
                            var i = arguments.length > 2 && void 0 !== arguments[2] && arguments[2];
                            if (this.style(this.cursor, {
                                    left: "".concat(e, "px")
                                }), this.params.showTime) {
                                var r = this.wavesurfer.getDuration(),
                                    s = this.wavesurfer.drawer.width / this.wavesurfer.params.pixelRatio,
                                    o = this.wavesurfer.drawer.getScrollX(),
                                    a = r / this.wavesurfer.drawer.width * o,
                                    n = Math.max(0, (e - this.wrapper.scrollLeft) / s * r) + a,
                                    l = this.formatTime(n);
                                i && (e -= this.displayTime.getBoundingClientRect().width), this.style(this.showTime, {
                                    left: "".concat(e, "px"),
                                    top: "".concat(t, "px")
                                }), this.style(this.displayTime, {
                                    visibility: "visible"
                                }), this.displayTime.innerHTML = "".concat(l)
                            }
                        }
                    }, {
                        key: "showCursor",
                        value: function() {
                            this.style(this.cursor, {
                                display: "flex"
                            }), this.params.showTime && this.style(this.showTime, {
                                display: "flex"
                            })
                        }
                    }, {
                        key: "hideCursor",
                        value: function() {
                            this.style(this.cursor, {
                                display: "none"
                            }), this.params.showTime && this.style(this.showTime, {
                                display: "none"
                            })
                        }
                    }, {
                        key: "formatTime",
                        value: function(e) {
                            return e = isNaN(e) ? 0 : e, this.params.formatTimeCallback ? this.params.formatTimeCallback(e) : [e].map((function(e) {
                                return [Math.floor(e % 3600 / 60), ("00" + Math.floor(e % 60)).slice(-2), ("000" + Math.floor(e % 1 * 1e3)).slice(-3)].join(":")
                            }))
                        }
                    }], o = [{
                        key: "create",
                        value: function(t) {
                            return {
                                name: "cursor",
                                deferInit: !(!t || !t.deferInit) && t.deferInit,
                                params: t,
                                staticProps: {},
                                instance: e
                            }
                        }
                    }], i && r(t.prototype, i), o && r(t, o), Object.defineProperty(t, "prototype", {
                        writable: !1
                    }), e
                }();
                t.default = a, e.exports = t.default
            }
        },
        t = {};
    var i = function i(r) {
        var s = t[r];
        if (void 0 !== s) return s.exports;
        var o = t[r] = {
            exports: {}
        };
        return e[r](o, o.exports, i), o.exports
    }(178);
    return i
})()));
//# sourceMappingURL=wavesurfer.cursor.min.js.map