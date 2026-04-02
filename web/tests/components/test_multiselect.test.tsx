import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MultiSelect } from '@/components/ui/multi-select';
import React from 'react';

// Mock components used inside MultiSelect if necessary, 
// though here we want to test the full behavior.
// We might need to mock the lucide icons if they cause issues, 
// but usually vitest handles them fine.

describe('MultiSelect Component', () => {
  const options = ['repo1', 'repo2', 'abc-repo'];
  const onChange = vi.fn();

  it('renders placeholder when no options are selected', () => {
    render(
      <MultiSelect 
        options={options} 
        selected={[]} 
        onChange={onChange} 
        placeholder="Select repos..." 
      />
    );
    expect(screen.getByText('Select repos...')).toBeDefined();
  });

  it('renders selected options as badges', () => {
    render(
      <MultiSelect 
        options={options} 
        selected={['repo1']} 
        onChange={onChange} 
      />
    );
    expect(screen.getByText('repo1')).toBeDefined();
  });

  it('opens dropdown and shows options when clicked', () => {
    render(
      <MultiSelect 
        options={options} 
        selected={[]} 
        onChange={onChange} 
      />
    );
    
    const trigger = screen.getByText('Select items...');
    fireEvent.click(trigger);
    
    expect(screen.getByPlaceholderText('Search repositories...')).toBeDefined();
    expect(screen.getByText('repo2')).toBeDefined();
    expect(screen.getByText('abc-repo')).toBeDefined();
  });

  it('filters options based on search query', () => {
    render(
      <MultiSelect 
        options={options} 
        selected={[]} 
        onChange={onChange} 
      />
    );
    
    fireEvent.click(screen.getByText('Select items...'));
    const input = screen.getByPlaceholderText('Search repositories...');
    
    fireEvent.change(input, { target: { value: 'abc' } });
    
    expect(screen.getByText('abc-repo')).toBeDefined();
    expect(screen.queryByText('repo1')).toBeNull();
  });

  it('calls onChange when an option is clicked', () => {
    render(
      <MultiSelect 
        options={options} 
        selected={['repo1']} 
        onChange={onChange} 
      />
    );
    
    fireEvent.click(screen.getByText('repo1')); // Open dropdown
    const option2 = screen.getByText('repo2');
    fireEvent.click(option2);
    
    expect(onChange).toHaveBeenCalledWith(['repo1', 'repo2']);
  });

  it('removes an option when the X button on the badge is clicked', () => {
    render(
      <MultiSelect 
        options={options} 
        selected={['repo1', 'repo2']} 
        onChange={onChange} 
      />
    );
    
    // Find the SVG/Button with X icon inside repo1 badge
    // In our implementation, it's a button with an X icon
    const repo1Badge = screen.getByText('repo1').closest('.inline-flex');
    const removeBtn = repo1Badge?.querySelector('button');
    
    if (removeBtn) {
      fireEvent.click(removeBtn);
    }
    
    expect(onChange).toHaveBeenCalledWith(['repo2']);
  });
});
