In TypeScript, you would define the types for the event, state, and props. Here is how you can convert your JavaScript code to TypeScript:

```tsx
import React, { useState, ChangeEvent } from 'react';

type Props = {};

const MyComponent: React.FC<Props> = () => {
  const [filter, setFilter] = useState<string>('');

  const handleSearch = (e: ChangeEvent<HTMLInputElement>) => {
    setFilter(e.target.value);
  };

  return (
    // Your JSX here
  );
};

export default MyComponent;
```

In this code, `ChangeEvent<HTMLInputElement>` is the type for the event `e`. The `useState<string>('')` indicates that the state `filter` is of type string. The `React.FC<Props>` indicates that the component `MyComponent` is a functional component that takes an object of type `Props` as its props.