"""
The feed module provides a high-level API for interacting
with a list of `ChatMessage` objects through the backend methods.
"""

from __future__ import annotations

import asyncio
import traceback

from inspect import (
    isasyncgen, isasyncgenfunction, isawaitable, isgenerator,
)
from io import BytesIO
from typing import (
    Any, BinaryIO, ClassVar, Dict, List, Type, Union,
)

import param

from .._param import Margin
from ..io.resources import CDN_DIST
from ..layout import Column, ListPanel
from ..layout.card import Card
from ..layout.spacer import VSpacer
from ..pane.image import SVG, ImageBase
from ..widgets.base import CompositeWidget
from ..widgets.button import Button
from .message import ChatMessage

Avatar = Union[str, BytesIO, ImageBase]
AvatarDict = Dict[str, Avatar]

USER_LOGO = "🧑"
ASSISTANT_LOGO = "🤖"
SYSTEM_LOGO = "⚙️"
ERROR_LOGO = "❌"
GPT_3_LOGO = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/ChatGPT_logo.svg/1024px-ChatGPT_logo.svg.png?20230318122128"
GPT_4_LOGO = "https://upload.wikimedia.org/wikipedia/commons/a/a4/GPT-4.png"
WOLFRAM_LOGO = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/WolframCorporateLogo.svg/1920px-WolframCorporateLogo.svg.png"

DEFAULT_AVATARS = {
    # User
    "client": USER_LOGO,
    "customer": USER_LOGO,
    "employee": USER_LOGO,
    "human": USER_LOGO,
    "person": USER_LOGO,
    "user": USER_LOGO,
    # Assistant
    "agent": ASSISTANT_LOGO,
    "ai": ASSISTANT_LOGO,
    "assistant": ASSISTANT_LOGO,
    "bot": ASSISTANT_LOGO,
    "chatbot": ASSISTANT_LOGO,
    "machine": ASSISTANT_LOGO,
    "robot": ASSISTANT_LOGO,
    # System
    "system": SYSTEM_LOGO,
    "exception": ERROR_LOGO,
    "error": ERROR_LOGO,
    # Human
    "adult": "🧑",
    "baby": "👶",
    "boy": "👦",
    "child": "🧒",
    "girl": "👧",
    "man": "👨",
    "woman": "👩",
    # Machine
    "chatgpt": GPT_3_LOGO,
    "gpt3": GPT_3_LOGO,
    "gpt4": GPT_4_LOGO,
    "dalle": GPT_4_LOGO,
    "openai": GPT_4_LOGO,
    "huggingface": "🤗",
    "calculator": "🧮",
    "langchain": "🦜",
    "translator": "🌐",
    "wolfram": WOLFRAM_LOGO,
    "wolfram alpha": WOLFRAM_LOGO,
    # Llama
    "llama": "🦙",
    "llama2": "🐪",
}

PLACEHOLDER_SVG = """
    <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-loader-3" width="40" height="40" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
        <path d="M3 12a9 9 0 0 0 9 9a9 9 0 0 0 9 -9a9 9 0 0 0 -9 -9"></path>
        <path d="M17 12a5 5 0 1 0 -5 5"></path>
    </svg>
"""  # noqa: E501


class ChatFeed(CompositeWidget):
    """
    A widget to display a list of `ChatMessage` objects and interact with them.

    This widget provides methods to:
    - Send (append) messages to the chat log.
    - Stream tokens to the latest `ChatMessage` in the chat log.
    - Execute callbacks when a user sends a message.
    - Undo a number of sent `ChatMessage` objects.
    - Clear the chat log of all `ChatMessage` objects.

    Reference: https://panel.holoviz.org/reference/chat/ChatFeed.html

    :Example:

    >>> async def say_welcome(contents, user, instance):
    >>>    yield "Welcome!"
    >>>    yield "Glad you're here!"

    >>> chat_feed = ChatFeed(callback=say_welcome, header="Welcome Feed")
    >>> chat_feed.send("Hello World!", user="New User", avatar="😊")
    """

    callback = param.Callable(
        allow_refs=False,
        doc="""
        Callback to execute when a user sends a message or
        when `respond` is called. The signature must include
        the previous message value `contents`, the previous `user` name,
        and the component `instance`.""",
    )

    callback_exception = param.ObjectSelector(
        default="summary",
        objects=["raise", "summary", "verbose", "ignore"],
        doc="""
        How to handle exceptions raised by the callback.
        If "raise", the exception will be raised.
        If "summary", a summary will be sent to the chat feed.
        If "verbose", the full traceback will be sent to the chat feed.
        If "ignore", the exception will be ignored.
        """,
    )

    callback_user = param.String(
        default="Assistant",
        doc="""
        The default user name to use for the message provided by the callback.""",
    )

    card_params = param.Dict(
        default={},
        doc="""
        Params to pass to Card, like `header`,
        `header_background`, `header_color`, etc.""",
    )

    message_params = param.Dict(
        default={},
        doc="""
        Params to pass to each ChatMessage, like `reaction_icons`, `timestamp_format`,
        `show_avatar`, `show_user`, and `show_timestamp`.""",
    )

    header = param.Parameter(
        doc="""
        The header of the chat feed; commonly used for the title.
        Can be a string, pane, or widget."""
    )

    margin = Margin(
        default=5,
        doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""",
    )

    renderers = param.HookList(
        doc="""
        A callable or list of callables that accept the value and return a
        Panel object to render the value. If a list is provided, will
        attempt to use the first renderer that does not raise an
        exception. If None, will attempt to infer the renderer
        from the value."""
    )

    placeholder_text = param.String(
        default="",
        doc="""
        If placeholder is the default LoadingSpinner,
        the text to display next to it.""",
    )

    placeholder_threshold = param.Number(
        default=1,
        bounds=(0, None),
        doc="""
        Min duration in seconds of buffering before displaying the placeholder.
        If 0, the placeholder will be disabled.""",
    )

    auto_scroll_limit = param.Integer(
        default=200,
        bounds=(0, None),
        doc="""
        Max pixel distance from the latest object in the Column to
        activate automatic scrolling upon update. Setting to 0
        disables auto-scrolling.""",
    )

    scroll_button_threshold = param.Integer(
        default=100,
        bounds=(0, None),
        doc="""
        Min pixel distance from the latest object in the Column to
        display the scroll button. Setting to 0
        disables the scroll button.""",
    )

    view_latest = param.Boolean(
        default=True,
        doc="""
        Whether to scroll to the latest object on init. If not
        enabled the view will be on the first object.""",
    )
    value = param.List(
        item_type=ChatMessage,
        doc="""
        The list of entries in the feed.""",
    )

    _placeholder = param.ClassSelector(
        class_=ChatMessage,
        allow_refs=False,
        doc="""
        The placeholder wrapped in a ChatMessage object;
        primarily to prevent recursion error in _update_placeholder.""",
    )

    _disabled = param.Boolean(
        default=False,
        doc="""
        Whether the chat feed is disabled.""",
    )

    _stylesheets: ClassVar[List[str]] = [f"{CDN_DIST}css/chat_feed.css"]

    _composite_type: ClassVar[Type[ListPanel]] = Card

    def __init__(self, **params):
        if params.get("renderers") and not isinstance(params["renderers"], list):
            params["renderers"] = [params["renderers"]]
        super().__init__(**params)
        # instantiate the card
        card_params = {
            "header": self.header,
            "hide_header": self.header is None,
            "collapsed": False,
            "collapsible": False,
            "css_classes": ["chat-feed"],
            "header_css_classes": ["chat-feed-header"],
            "title_css_classes": ["chat-feed-title"],
            "sizing_mode": self.sizing_mode,
            "height": self.height,
            "width": self.width,
            "max_width": self.max_width,
            "max_height": self.max_height,
            "styles": {
                "border": "1px solid var(--panel-border-color, #e1e1e1)",
                "padding": "0px",
            },
            "stylesheets": self._stylesheets,
        }
        card_params.update(**self.card_params)
        if self.sizing_mode is None:
            card_params["height"] = card_params.get("height", 500)
        self._composite.param.update(**card_params)

        # instantiate the card's column
        chat_log_params = {
            p: getattr(self, p)
            for p in Column.param
            if (p in ChatFeed.param and p != "name" and getattr(self, p) is not None)
        }
        chat_log_params["css_classes"] = ["chat-feed-log"]
        chat_log_params["stylesheets"] = self._stylesheets
        chat_log_params["objects"] = self.value
        chat_log_params["margin"] = 0
        self._chat_log = Column(**chat_log_params)
        self._composite[:] = [self._chat_log, VSpacer()]

        # handle async callbacks using this trick
        self._callback_trigger = Button(visible=False)
        self._callback_trigger.on_click(self._prepare_response)

        self.link(self._chat_log, value="objects", bidirectional=True)

    @param.depends("placeholder_text", watch=True, on_init=True)
    def _update_placeholder(self):
        loading_avatar = SVG(
            PLACEHOLDER_SVG, sizing_mode=None, css_classes=["rotating-placeholder"]
        )
        self._placeholder = ChatMessage(
            user=" ",
            value=self.placeholder_text,
            show_timestamp=False,
            avatar=loading_avatar,
            reaction_icons={},
            show_copy_icon=False,
        )

    @param.depends("header", watch=True)
    def _hide_header(self):
        """
        Hide the header if there is no title or header.
        """
        self._composite.hide_header = not self.header

    def _replace_placeholder(self, message: ChatMessage | None = None) -> None:
        """
        Replace the placeholder from the chat log with the message
        if placeholder, otherwise simply append the message.
        Replacing helps lessen the chat log jumping around.
        """
        index = None
        if self.placeholder_threshold > 0:
            try:
                index = self.value.index(self._placeholder)
            except ValueError:
                pass

        if index is not None:
            if message is not None:
                self._chat_log[index] = message
            elif message is None:
                self._chat_log.remove(self._placeholder)
        elif message is not None:
            self._chat_log.append(message)

    def _build_message(
        self,
        value: dict,
        user: str | None = None,
        avatar: str | BinaryIO | None = None,
    ) -> ChatMessage | None:
        """
        Builds a ChatMessage from the value.
        """
        if "value" not in value:
            raise ValueError(
                f"If 'value' is a dict, it must contain a 'value' key, "
                f"e.g. {{'value': 'Hello World'}}; got {value!r}"
            )
        message_params = dict(value, renderers=self.renderers, **self.message_params)
        if user:
            message_params["user"] = user
        if avatar:
            message_params["avatar"] = avatar
        if self.width:
            message_params["width"] = int(self.width - 80)
        message = ChatMessage(**message_params)
        return message

    def _upsert_message(
        self, value: Any, message: ChatMessage | None = None
    ) -> ChatMessage | None:
        """
        Replace the placeholder message with the response or update
        the message's value with the response.
        """
        if value is None:
            # don't add new message if the callback returns None
            return

        user = self.callback_user
        avatar = None
        if isinstance(value, dict):
            user = value.get("user", user)
            avatar = value.get("avatar")
        if message is not None:
            message.update(value, user=user, avatar=avatar)
            return message
        elif isinstance(value, ChatMessage):
            return value

        if not isinstance(value, dict):
            value = {"value": value}
        new_message = self._build_message(value, user=user, avatar=avatar)
        self._replace_placeholder(new_message)
        return new_message

    def _extract_contents(self, message: ChatMessage) -> Any:
        """
        Extracts the contents from the message's panel object.
        """
        value = message._value_panel
        if hasattr(value, "object"):
            contents = value.object
        elif hasattr(value, "objects"):
            contents = value.objects
        elif hasattr(value, "value"):
            contents = value.value
        else:
            contents = value
        return contents

    async def _serialize_response(self, response: Any) -> ChatMessage | None:
        """
        Serializes the response by iterating over it and
        updating the message's value.
        """
        response_message = None
        if isasyncgen(response):
            async for token in response:
                response_message = self._upsert_message(token, response_message)
        elif isgenerator(response):
            for token in response:
                response_message = self._upsert_message(token, response_message)
        elif isawaitable(response):
            response_message = self._upsert_message(await response, response_message)
        else:
            response_message = self._upsert_message(response, response_message)
        return response_message

    async def _handle_callback(self, message: ChatMessage) -> ChatMessage | None:
        contents = self._extract_contents(message)
        response = self.callback(contents, message.user, self)
        response_message = await self._serialize_response(response)
        return response_message

    async def _schedule_placeholder(
        self,
        task: asyncio.Task,
        num_entries: int,
    ) -> None:
        """
        Schedules the placeholder to be added to the chat log
        if the callback takes longer than the placeholder threshold.
        """
        if self.placeholder_threshold == 0:
            return

        callable_is_async = asyncio.iscoroutinefunction(
            self.callback
        ) or isasyncgenfunction(self.callback)
        start = asyncio.get_event_loop().time()
        while not task.done() and num_entries == len(self._chat_log):
            duration = asyncio.get_event_loop().time() - start
            if duration > self.placeholder_threshold or not callable_is_async:
                self._chat_log.append(self._placeholder)
                return
            await asyncio.sleep(0.28)

    async def _prepare_response(self, _) -> None:
        """
        Prepares the response by scheduling the placeholder and
        executing the callback.
        """
        if self.callback is None:
            return

        disabled = self.disabled
        try:
            self.disabled = True
            message = self._chat_log[-1]
            if not isinstance(message, ChatMessage):
                return

            num_entries = len(self._chat_log)
            task = asyncio.create_task(self._handle_callback(message))
            await self._schedule_placeholder(task, num_entries)
            await task
            task.result()
        except Exception as e:
            send_kwargs = dict(user="Exception", respond=False)
            if self.callback_exception == "summary":
                self.send(str(e), **send_kwargs)
            elif self.callback_exception == "verbose":
                self.send(f"```python\n{traceback.format_exc()}\n```", **send_kwargs)
            elif self.callback_exception == "ignore":
                return
            else:
                raise e
        finally:
            self._replace_placeholder(None)
            self.disabled = disabled

    # Public API

    def send(
        self,
        value: ChatMessage | dict | Any,
        user: str | None = None,
        avatar: str | BinaryIO | None = None,
        respond: bool = True,
    ) -> ChatMessage | None:
        """
        Sends a value and creates a new message in the chat log.

        If `respond` is `True`, additionally executes the callback, if provided.

        Arguments
        ---------
        value : ChatMessage | dict | Any
            The message contents to send.
        user : str | None
            The user to send as; overrides the message message's user if provided.
        avatar : str | BinaryIO | None
            The avatar to use; overrides the message message's avatar if provided.
        respond : bool
            Whether to execute the callback.

        Returns
        -------
        The message that was created.
        """
        if isinstance(value, ChatMessage):
            if user is not None or avatar is not None:
                raise ValueError(
                    "Cannot set user or avatar when explicitly sending "
                    "a ChatMessage. Set them directly on the ChatMessage."
                )
            message = value
        else:
            if not isinstance(value, dict):
                value = {"value": value}
            message = self._build_message(value, user=user, avatar=avatar)
        self._chat_log.append(message)
        if respond:
            self.respond()
        return message

    def stream(
        self,
        value: str,
        user: str | None = None,
        avatar: str | BinaryIO | None = None,
        message: ChatMessage | None = None,
    ) -> ChatMessage | None:
        """
        Streams a token and updates the provided message, if provided.
        Otherwise creates a new message in the chat log, so be sure the
        returned message is passed back into the method, e.g.
        `message = chat.stream(token, message=message)`.

        This method is primarily for outputs that are not generators--
        notably LangChain. For most cases, use the send method instead.

        Arguments
        ---------
        value : str | dict | ChatMessage
            The new token value to stream.
        user : str | None
            The user to stream as; overrides the message's user if provided.
        avatar : str | BinaryIO | None
            The avatar to use; overrides the message's avatar if provided.
        message : ChatMessage | None
            The message to update.

        Returns
        -------
        The message that was updated.
        """
        if isinstance(value, ChatMessage) and (user is not None or avatar is not None):
            raise ValueError(
                "Cannot set user or avatar when explicitly streaming "
                "a ChatMessage. Set them directly on the ChatMessage."
            )
        elif message:
            if isinstance(value, (str, dict)):
                message.stream(value)
                if user:
                    message.user = user
                if avatar:
                    message.avatar = avatar
            else:
                message.update(value, user=user, avatar=avatar)
            return message

        if isinstance(value, ChatMessage):
            message = value
        else:
            if not isinstance(value, dict):
                value = {"value": value}
            message = self._build_message(value, user=user, avatar=avatar)
        self._replace_placeholder(message)
        return message

    def respond(self):
        """
        Executes the callback with the latest message in the chat log.
        """
        self._callback_trigger.param.trigger("clicks")

    def undo(self, count: int = 1) -> List[Any]:
        """
        Removes the last `count` of entries from the chat log and returns them.

        Parameters
        ----------
        count : int
            The number of entries to remove, starting from the last message.

        Returns
        -------
        The entries that were removed.
        """
        if count <= 0:
            return []
        entries = self._chat_log.objects
        undone_entries = entries[-count:]
        self._chat_log.objects = entries[:-count]
        return undone_entries

    def clear(self) -> List[Any]:
        """
        Clears the chat log and returns the entries that were cleared.

        Returns
        -------
        The entries that were cleared.
        """
        cleared_entries = self._chat_log.objects
        self._chat_log.clear()
        return cleared_entries
