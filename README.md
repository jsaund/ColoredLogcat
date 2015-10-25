## What's ColoredLogcat
ColoredLogcat takes the adb logcat output and improves it's readability.

The output is formatted to quickly identify logs associated with particular tags and the priority level they are associated with.

This dramatically improves the ability to sift through the wealth of information dumped to the screen and pick out the information that pertains to your application.

## Usage
### Unfiltered
Run colored logcat from the terminal or command prompt.

```./coloredlogcat.py```

### Filtering your package name
To obtain just the information associated with your process you can run colored logcat by specifying the package name you are interested in filtering.

```./coloredlogcat.py [com.your.package]```

### Custom Filtering using Pipes
You can completely customize the filtering operation by piping the result from either a file or directly from 'adb logcat -v time'.

```adb logcat -v time MyTagOne:V MyTagTwo:V *:S | grep "some text" | ./coloredlogcat.py```

```cat my_logs.txt | ./coloredlogcat.py```

## Requirements
- Python 2.7.6+
- ADB 1.0.31

## License
ColoredLogcat is availble under the Apache 2.0 License.

## TODO
- Add support for filtering on tags
- Add support for filtering on wildcards in log body
