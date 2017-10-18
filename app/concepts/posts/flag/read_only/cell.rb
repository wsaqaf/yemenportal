class Posts::Flag::ReadOnly::Cell < Posts::Flag::Cell
  private

  def button
    content_tag(:div, class: ["post-flag", zero_flags_class]) do
      content_tag(:div, class: ["post-flag__element"], style: "background-color: #{color}") do
        yield
      end
    end
  end

  def zero_flags_class
    if number_of_reviews_for_post.zero?
      "post-flag--zero"
    end
  end
end
