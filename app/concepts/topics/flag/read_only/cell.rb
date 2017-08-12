class Topics::Flag::ReadOnly::Cell < Topics::Flag::Cell
  private

  def button
    content_tag(:div, class: ["topic-flag", zero_flags_class]) do
      content_tag(:div, class: ["topic-flag__element"], style: "background-color: #{flag.color}") do
        yield
      end
    end
  end

  def zero_flags_class
    if flag.number_of_reviews_for_topic.zero?
      "topic-flag--zero"
    end
  end
end
