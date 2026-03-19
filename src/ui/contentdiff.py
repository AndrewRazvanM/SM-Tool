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