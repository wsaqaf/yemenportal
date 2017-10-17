class Posts::Filter
  def initialize(params)
    @params = Params.new(params)
  end

  def filtered_posts
    filters.reduce(all_posts) do |posts, filter|
      filter.call(posts)
    end
  end

  private

  attr_reader :params

  def all_posts
    ::Post.all
  end

  # More filters will be added later
  def filters
    [page_filter]
  end

  def page_filter
    ->(posts) { posts.paginate(page: params.page) }
  end

  def time_filter
    if params.all_time?
      ->(topics) { topics }
    else
      ->(topics) { topics.created_later_than(beginning_time_from_params) }
    end
  end

  def beginning_time_from_params
    case params.time.to_sym
    when :daily
      1.day.ago
    when :weekly
      7.days.ago
    when :monthly
      1.month.ago
    end
  end

  def sorting_filter
    case params.set.to_sym
    when :new
      ->(topics) { topics.ordered_by_date }
    when :highly_voted
      ->(topics) { topics.ordered_by_voting_result.ordered_by_date }
    when :most_covered
      ->(topics) { topics.ordered_by_size.ordered_by_voting_result.ordered_by_date }
    end
  end
end
