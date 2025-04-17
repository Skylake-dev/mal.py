from datetime import datetime
from typing import List, Optional

from .base import PaginatedObject, ReadOnlyIterable

from .typed import (
    SubBoardPayload,
    BoardPayload,
    BoardCategoryPayload,
    TopicPayload,
    ForumTopicsPayload,
    ForumUserPayload,
    PollOptionPayload,
    PollPayload,
    ForumPostPayload,
    DiscussionPayload,
    TopicDetailPayload
)


class SubBoard:
    """Represent a subboard of a forum board.

    Attributes:
        id: the id of the subboard
        title: the title of the subboard
    """

    def __init__(self, data: SubBoardPayload) -> None:
        self.id: int = data['id']
        self.title: str = data['title']

    def __str__(self) -> str:
        return f'Subboard {self.id}: {self.title}'


class Board:
    """Represents a forum board.

    Attributes:
        id: the id of the board
        title: the title of the board
        description: the description of the board
        subboards: list of all the subboards of the current board
    """

    def __init__(self, data: BoardPayload) -> None:
        self.id: int = data['id']
        self.title: str = data['title']
        self.description: str = data['description']
        self.subboards: List[SubBoard] = []
        for subboard in data['subboards']:
            self.subboards.append(SubBoard(subboard))

    def __str__(self) -> str:
        s = f'Board {self.id}: {self.title}\n{self.description}\n'
        s += '\n'.join([str(sub) for sub in self.subboards])
        return s


class BoardCategory(ReadOnlyIterable[Board]):
    """Boards grouped by category. Directly iterate over this object to retrieve all boards.

    Attributes:
        title: the name of this cateogry
        boards: list of boards belonging to this category
    """

    def __init__(self, data: BoardCategoryPayload) -> None:
        self.title: str = data['title']
        self.boards: List[Board] = []
        # satisfy the ReadOnlyProtocol structure
        self._list = self.boards
        for board in data['boards']:
            self.boards.append(Board(board))

    def __str__(self) -> str:
        s = f'Category: {self.title}'
        s += '\n'.join([str(board) for board in self.boards])
        return s


class Topic:
    """Represent a forum topic.

    Attributes:
        id: the id of the topic
        title: description for this topic
        created_by: name of the user who created the topic
        number_of_posts: the number of posts under this topic
        last_post_created_by: name of the user who created the last post
        is_locked: whether the post is locked
    """

    def __init__(self, data: TopicPayload) -> None:
        self.id: int = data['id']
        self.title: str = data['title']
        self._created_at: str = data['created_at']
        self.created_by: str = data['created_by']['name']
        self.number_of_posts: int = data['number_of_posts']
        self._last_post_created_at: str = data['last_post_created_at']
        self.last_post_created_by: str = data['last_post_created_by']['name']
        self.is_locked: bool = data['is_locked']

    def __str__(self) -> str:
        topic = f'{self.id}: "{self.title}" created at: {self._created_at} posts:{self.number_of_posts}'
        return topic

    @property
    def created_at(self) -> datetime:
        """ISO 8061 datetime of when the topic was created."""
        return datetime.fromisoformat(self._created_at)

    @property
    def last_post_created_at(self) -> datetime:
        """ISO 8061 datetime of when last post in this topic was created"""
        return datetime.fromisoformat(self._last_post_created_at)


class ForumTopics(PaginatedObject, ReadOnlyIterable[Topic]):
    """Results of a topic query. Contains the resulting topics.
    Directly iterate over this object to retrieve all the topics.

    Attributes:
        query: query that gave these results
        raw: The raw json data for this object as returned by the API.
    """

    def __init__(self, data: ForumTopicsPayload, query: str) -> None:
        super().__init__(data)
        self.query: str = query
        self._list: List[Topic] = []
        for topic in data['data']:
            self._list.append(Topic(topic))
        self.raw: ForumTopicsPayload = data

    def __str__(self) -> str:
        if self.query:
            s = f'Topics for the query "{self.query}:"\n'
        else:
            s = f'Topics:\n'
        s += '\n'.join([str(topic) for topic in self._list])
        return s


class ForumUser:
    """Represents a forum user.

    Attributes:
        id: id of the user
        name: nickname of the user
        avatar: url to the profile picture used in the forum
    """

    def __init__(self, data: ForumUserPayload) -> None:
        self.id: int = data['id']
        self.name: str = data['name']
        self.avatar: str = data['forum_avator']

    def __str__(self) -> str:
        return self.name


class PollOption:
    """Represents an option in a poll.

    Attributes:
        id: id of this option
        text: the text of this option
        votes: number of votes for this option
    """

    def __init__(self, data: PollOptionPayload) -> None:
        self.id: int = data['id']
        self.text: str = data['text']
        self.votes: int = data['votes']

    def __str__(self) -> str:
        return f'{self.text} - {self.votes} votes'


class Poll(ReadOnlyIterable[PollOption]):
    """Represents a poll posted on the forum. Directly iterate over this object to retrive
    all poll options.

    Attributes:
        id: id of the poll
        question: the question of the poll
        closed: whether the poll is closed or not
        options: list of options
    """

    def __init__(self, data: PollPayload) -> None:
        self.id: int = data['id']
        self.question: str = data['question']
        self.closed: bool = data['closed']
        self.options: List[PollOption] = []
        # satisfy the ReadOnlyProtocol structure
        self._list = self.options
        for option in data['options']:
            self.options.append(PollOption(option))

    def __str__(self) -> str:
        s = f'Poll: {self.question}:\n'
        s += '\n'.join([str(option) for option in self.options])
        return s

    @property
    def num_options(self) -> int:
        """The number of options available."""
        return len(self.options)

    @property
    def total_votes(self) -> int:
        """Total number of votes in this poll across all options."""
        return sum([option.votes for option in self.options])

    @property
    def winner(self) -> PollOption:
        """Returns the option that is currently winning. It is the definitive winner
        if the poll is closed.
        """
        return max(self.options, key=lambda item: item.votes)


class ForumPost:
    """Represents a post on a board.

    Attributes:
        id: id of the post
        number: the post number in the discussion, is assigned in order of reply
        created_by: the user who created this post
        body: the text of the post
        signature: the signature of the author of this post
    """

    def __init__(self, data: ForumPostPayload) -> None:
        self.id: int = data['id']
        self.number: int = data['number']
        self._created_at: str = data['created_at']
        self.created_by: ForumUser = ForumUser(data['created_by'])
        self.body: str = data['body']
        self.signature: str = data['signature']

    def __str__(self) -> str:
        return f'#{self.number} {self.created_by.name} commented:\n{self.body}'

    @property
    def created_at(self) -> datetime:
        """ISO 8061 datetime of when the post was created."""
        return datetime.fromisoformat(self._created_at)


class Discussion(ReadOnlyIterable[ForumPost]):
    """Represents a discussion on a board. Directly iterate over this object to retrieve
    all posts.

    Attributes:
        title: the title of the discussion
        posts: list of all posts under this discussion
        poll: optional, poll in this discussio
        raw: The raw json data for this object as returned by the API.
    """

    def __init__(self, data: DiscussionPayload) -> None:
        self.title: str = data['title']
        self.posts: List[ForumPost] = []
        # satisfy the ReadOnlyProtocol structure
        self._list = self.posts
        for post in data['posts']:
            self.posts.append(ForumPost(post))
        # sort by number so that the discussion is printed in order
        # it should not be necessary in theory
        self.posts.sort(key=lambda item: item.number)
        self.poll: Optional[Poll] = None
        if 'poll' in data:
            self.poll = Poll(data['poll'])
        self.raw: DiscussionPayload = data

    def __str__(self) -> str:
        s = f'Discussion: "{self.title}":\n'
        s += '\n'.join([str(post) for post in self.posts])
        s += '\nAttached polls:\n'
        s += str(self.poll)
        return s

    @property
    def num_posts(self) -> int:
        """Shorthand for len(discussion.posts)."""
        return len(self.posts)


class TopicDetail(PaginatedObject, ReadOnlyIterable[Discussion]):
    """Results for a topic detail query. Contains the discussions under this topic.
    Directly iterate over this object to retrieve all discussions

    Attributes:
        raw: The raw json data for this object as returned by the API.
        discussions: list of discussions on this topic.
    """

    def __init__(self, data: TopicDetailPayload) -> None:
        super().__init__(data)
        self.discussions: List[Discussion] = []
        # satisfy the ReadOnlyProtocol structure
        self._list = self.discussions
        for discussion in data['data']:
            self.discussions.append(Discussion(discussion))
        self.raw: TopicDetailPayload = data

    def __str__(self) -> str:
        return '\n'.join([str(disc) for disc in self.discussions])
