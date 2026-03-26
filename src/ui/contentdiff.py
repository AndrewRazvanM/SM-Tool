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
        self.row_content= content[:]  # avoid aliasing

class ScrollWinContentDiff:
    __slots__ = (
        "is_content_diff",
        "_pid_map",
        "_seen_pids",
        "_prev_order",
        "force_write",
    )

    def __init__(self):
        self.is_content_diff = []
        self._pid_map = {}
        self._seen_pids = set()
        self._prev_order = []     # previous frame PID order
        self.force_write = False

    def check_differences(self, visible_rows: list[list]):
        render_list = self.is_content_diff
        pid_map = self._pid_map
        seen = self._seen_pids
        prev_order = self._prev_order

        seen.clear()

        # Ensure render_list is large enough
        if len(render_list) < len(visible_rows):
            render_list.extend([None] * (len(visible_rows) - len(render_list)))

        for row_index, row in enumerate(visible_rows):
            pid = row[0].value
            starttime = row[11].value
            seen.add(pid)

            entry = pid_map.get(pid)

            # New process or PID recycled
            if (
                entry is None
                or entry.starttime != starttime
                or self.force_write
            ):
                entry = ScrollWinDiffList(row)
                pid_map[pid] = entry
                render_list[row_index] = entry
                continue

            # Detect scroll movement
            moved = (
                row_index >= len(prev_order)
                or prev_order[row_index] != pid
            )

            # Detect value changes
            values_changed = (
                row[7].value != entry.row_content[7].value or
                row[8].value != entry.row_content[8].value or
                row[9].value != entry.row_content[9].value or
                row[4].value != entry.row_content[4].value or
                row[3].value != entry.row_content[3].value or
                row[5].value != entry.row_content[5].value
            )

            entry.row_changed = moved
            entry.row_update_values = (not moved) and values_changed

            if values_changed:
                entry.row_content[7] = row[7]
                entry.row_content[8] = row[8]
                entry.row_content[9] = row[9]
                entry.row_content[4] = row[4]
                entry.row_content[3] = row[3]
                entry.row_content[5] = row[5]

            render_list[row_index] = entry

        # Trim render list if fewer rows visible
        del render_list[len(visible_rows):]

        # Remove dead processes
        for pid in list(pid_map.keys()):
            if pid not in seen:
                del pid_map[pid]

        # Save PID order for next frame
        self._prev_order = [row[0].value for row in visible_rows]

        self.force_write = False