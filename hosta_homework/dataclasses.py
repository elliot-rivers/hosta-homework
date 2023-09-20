import dataclasses
import typing


class FromDict:

    @classmethod
    def from_dict(cls: type, data: dict):
        """Construct a dataclass from a dictionary containing (at least) its fields

        Arguments:
            cls (type): The type this classmethod operates on
            data (dict): A dict containing fields 

        Returns:
            An instance of cls

        Rationale:
            Reduce boiler-plate code to construct dataclasses.
            Handle lists of objects correctly; something a naive `cls(**data)` will not do.
            This mechanism also works if you over-specify the input dict;
                Probably not good for a general data model, but for the sake of this submission,
                `cls(**data)` is too naive in this way

        Usage: 
            @dataclasses.dataclass
            class MyClass(FromDict):
                foo: str
                bar: int

            data = {"foo": "hello", "bar": 1234}
            c = MyClass.from_dict(data)

        Future work: 
            Test and handle other objects than lists/dicts; the only ones needed in this submission

            Or find a 3rd-party library to just do this instead
        """
        def _from_dict_helper(cls, data):
            try:
                return cls.from_dict(data)
            except AttributeError:
                return cls(data)

        args = {}
        for name, field in cls.__dataclass_fields__.items():
            # Special-handling for (typing) generic objects
            type_ = field.type
            try:
                match len(type_.__args__):
                    case 1:
                        value = type_.__origin__(_from_dict_helper(type_.__args__[0], d) for d in data[field.name])
                    case 2:
                        value = type_.__origin__({
                            _from_dict_helper(type_.__args__[0], k) : _from_dict_helper(type_.__args[1], v)
                                for k, v in data[field.name].items()
                        })

            except AttributeError:
                # It's just a regular ol' type
                value = _from_dict_helper(type_, data[field.name])

            args[name] = value

        return cls(**args)



