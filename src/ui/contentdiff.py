class DiffList:

    __slots__= (
        "changed",
        "content",
        "prev_value",
        "prev_bar_width"
    )

    def __init__(self, content: object) -> object:
        self.changed= True
        self.prev_value= content.value
        self.prev_bar_width= content.bar_width
        self.content= content

class ContentDiff:

    __slots__ = (
        "is_content_diff",
        "force_write"
    )

    def __init__(self):
        self.is_content_diff= []
        self.force_write= False
    
    def check_differences(self, content_list: list):
        """
        Check if the MemTotal, MemFree etc changed".
            Returns a list of objects (bool, object from formatter). 
                True for content changing.
                False for it not changing.
        """
        is_content_diff= self.is_content_diff

        #on initial run, build the list then cache it
        if is_content_diff == []:
            for content in content_list:
                is_content_diff.append(DiffList(content))

            return
        
        if self.force_write:
            for index, content in enumerate(content_list):
                entry = is_content_diff[index]
                entry.changed = True
                entry.content = content
                entry.prev_value = content.value
                entry.prev_bar_width = content.bar_width
                
            self.force_write= False
            return

        else:
            for index, content in enumerate(content_list):
                if content.value != is_content_diff[index].prev_value or content.bar_width != is_content_diff[index].prev_bar_width:
                    is_content_diff[index].content= content_list[index]
                    is_content_diff[index].changed= True
                    is_content_diff[index].prev_value= content.value 
                    is_content_diff[index].prev_bar_width= content.bar_width

                else:
                    is_content_diff[index].changed= False

        self.is_content_diff= is_content_diff

class ScrollWinDiffList:

    __slots__= (
        "row_changed",
        "row_update_values",
        "row_content",
        "prev_pid",
        "starttime", #used to check if the PID was recycled
    )

    def __init__(self, content: list):
        self.row_changed= True
        self.row_update_values= False
        self.prev_pid= content[0].value
        self.starttime= content[11].value
        self.row_content= content

class ScrollWinContentDiff:
    """
    Content Diff engine for scrollable windows, like the processes or I/O (when it's implemented).
    """

    __slots__ = (
        "is_content_diff",
        "force_write"
    )

    def __init__(self):
        self.is_content_diff= []
        self.force_write= False
    
    def check_differences(self, visible_content_list: list):
        """
        Check if the MemTotal, MemFree etc changed".
            Returns a list of objects (bool, object from formatter). 
                True for content changing.
                False for it not changing.
        """
        diff = self.is_content_diff
        diff_len= len(diff)
        content_list_len= len(visible_content_list)

        # first run
        if not diff:
            for content in visible_content_list:
                diff.append(ScrollWinDiffList(content))
            return

        if self.force_write:
            for index, content in enumerate(visible_content_list):
                if index >= diff_len:
                    diff.append(ScrollWinDiffList(content))
                else:
                    entry = diff[index]
                    entry.row_changed = True
                    entry.row_update_values = False
                    entry.row_content = content
                    entry.prev_pid = content[0].value
                    entry.starttime = content[11].value

            self.force_write = False
            return

        # trim excess rows
        if diff_len > content_list_len:
            del diff[content_list_len:]

        # check differences
        for index, content in enumerate(visible_content_list):
            if index >= diff_len:
                diff.append(ScrollWinDiffList(content))
                continue

            entry = diff[index]
            if content[0].value != entry.prev_pid or content[11].value != entry.starttime:
                entry.row_changed = True
                entry.row_update_values = False
                entry.row_content = content
                entry.prev_pid = content[0].value
                entry.starttime = content[11].value
            else:
                entry.row_changed = False
                entry.row_update_values = True
                entry.row_content[7] = content[7] #updates only cpu
                entry.row_content[9] = content[9] #updates only mem
                entry.row_content[8] = content[8] #updates only virt mem
                entry.row_content[4] = content[4] #updates only state
                entry.row_content[3] = content[3] #updates only priority
                entry.row_content[5] = content[5] #updates only time
